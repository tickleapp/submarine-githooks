#
# Copyright 2015 Tickle Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import unicode_literals, division, absolute_import, print_function
from importlib import import_module
import os
import sys
import six
from taskr import console
from taskr.contrib.git import GitRepo
import yaml
from submarine_githooks.checker import Checker
from submarine_githooks.constants import hook_names
from submarine_githooks.content import Content


def main():
    # Get options and constants ========================================================================================

    # Find source root
    callee = os.path.relpath(sys.argv[0])
    if callee.startswith('.git/hooks'):
        # from `.git/hooks/pre-commit`
        source_root = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..', '..'))
        hook_name = os.path.split(sys.argv[0])[-1]
    else:
        # Call directly
        source_root = os.getcwd()
        while not os.path.exists(os.path.join(source_root, '.git')):
            if source_root == '/':
                console.error('Cannot find .git directory.')
                exit(1)

            source_root = os.path.abspath(os.path.join(source_root, '..'))

        hook_name = sys.argv[1] if len(sys.argv) > 1 else 'pre-commit'

    if hook_name not in hook_names:
        console.error('Invalid hook name. got "{}" Choices={{{}}}'.format(hook_name, ','.join(hook_names)))
        exit(1)

    # Define constants
    git_hooks_home = os.path.join(source_root, '.githooks')
    git_repo = GitRepo(source_root)
    # setup python path
    sys.path.append(git_hooks_home)
    checkers_package_dir = git_hooks_home

    config = {
        'debug': False
    }
    # read options from file
    local_config_path = os.path.join(git_hooks_home, 'config.yaml')
    if not os.path.exists(local_config_path):
        local_config_path = os.path.splitext(local_config_path)[0] + '.json'
    if os.path.exists(local_config_path):
        with open(local_config_path, 'r') as f:
            config.update(yaml.load(f))
    # read options from env
    env_option_prefix = 'SUBMARINE_GITHOOK_'
    bool_env_options = ('debug',)
    for key, value in six.iteritems(os.environ):
        if key.startswith(env_option_prefix):
            key = key[len(env_option_prefix):].lower()
            if key in bool_env_options:
                try:
                    value = int(value) != 0
                except ValueError:
                    value = bool(value)
                finally:
                    config[key] = value

    debug = config['debug']
    if debug:
        console.info('Found .git at {}'.format(source_root))
        if os.path.exists(local_config_path):
            console.info('Loaded config from {}'.format(local_config_path))

    # Find checkers ====================================================================================================
    if debug:
        console.show('')
        console.info('Load checkers for {}'.format(hook_name), bar_width=120)
    checkers = []
    """:type: list[Checker]"""
    for checker_path in os.listdir(checkers_package_dir):
        if checker_path.endswith('.py') and checker_path != '__init__.py':
            checker_module_str = os.path.splitext(checker_path)[0]
            checker_module = import_module(checker_module_str)
            for attr in dir(checker_module):
                checker = getattr(checker_module, attr)
                if isinstance(checker, Checker) and checker.is_active_for_hook(hook_name):
                    checkers.append(checker)

    if not checkers:
        if debug:
            console.warn('No checkers for {}'.format(hook_name))
    if debug:
        for checker in checkers:
            console.success('Found checker: {}'.format(checker.name))

    # Find content to be checked =======================================================================================
    if debug:
        console.show('')
        console.info('Load contents for {}'.format(hook_name), bar_width=120)
    contents = []
    """:type: list[Content]"""
    if hook_name == 'pre-commit':
        for file_path, (status_staged, status_working) in git_repo.status.items():
            if status_staged in 'TMARC':
                content = Content.create_with_hook(hook_name, file_path)
                if content:
                    contents.append(content)
    elif hook_name == 'commit-msg':
        commit_message_file_path = sys.argv[-1]
        content = Content.create_with_hook(hook_name, commit_message_file_path)
        if content:
            contents.append(content)
    elif hook_name == 'post-checkout':
        orig_commit_id, dest_commit_id, branch_checkout = sys.argv[1:]
        branch_checkout = branch_checkout == '1'
        if branch_checkout:
            for changed_file in git_repo.changed_files(orig_commit_id, dest_commit_id):
                file_path = os.path.relpath(os.path.join(git_repo.source_root, changed_file), git_repo.source_root)
                content = Content.create_with_hook(hook_name, file_path, orig_commit_id, dest_commit_id)
                if content:
                    contents.append(content)
    elif hook_name == 'post-merge':
        source_commit = None
        source_branch = None
        squash_merge = sys.argv[-1] == '1'
        for key, value in os.environ.items():
            if key.startswith('GITHEAD_') and len(key) == 48:
                source_commit = key[8:]
                source_branch = value
        if source_commit and source_branch:
            for file_path in git_repo.changed_files(commit=source_commit):
                content = Content.create_with_hook(hook_name, file_path, source_commit, squash_merge)
                if content:
                    contents.append(content)
    elif hook_name == 'pre-push':
        remote_name, remote_url = sys.argv[1:]

        for reference_info_str in sys.stdin.read().splitlines():
            local_ref, local_commit_id, remote_ref, remote_commit_id = reference_info_str.strip().split(' ')
            branch_deleted_from_local = local_commit_id == '0'*40
            new_branch_to_remote = remote_commit_id == '0'*40
            content = Content.create_with_hook(hook_name,
                                               remote_name, remote_url,
                                               local_ref, local_commit_id,
                                               remote_ref, remote_commit_id,
                                               branch_deleted_from_local,
                                               new_branch_to_remote)
            if content:
                contents.append(content)

    if not contents:
        if debug:
            console.warn('No content to check for {}'.format(hook_name))
    if debug:
        for content in contents:
            console.success(content.discovered_message())

    # Go, start to check ===============================================================================================
    if debug:
        console.show('')
        console.info('Start check for {}'.format(hook_name), bar_width=120)
    exit_code = 0
    for checker in checkers:
        if checker.once:
            # noinspection PyBroadException
            try:
                checker(git_repo, hook_name, map(lambda _content: _content.arguments, contents))
            except Exception as e:
                console.error('{} hook fails\nchecker: {}\n{}'.format(hook_name, checker.name, str(e)))
                exit_code |= 1
            else:
                if debug:
                    console.success('{} checker success'.format(checker.name))
        else:
            for content in contents:
                args = (git_repo, hook_name) + content.arguments
                if content.file_path and not checker.is_active_for_file(content.file_path):
                    if debug:
                        console.success(content.inactive_message(checker))
                    continue
                # noinspection PyBroadException
                try:
                    checker(*args)
                except Exception as e:
                    console.show('')
                    console.error('{} hook fails\nchecker: {}\n{}'.format(hook_name,
                                                                  checker.name,
                                                                  content.error_message(checker, e)))
                    exit_code |= 1
                else:
                    if debug:
                        console.success(content.success_message(checker))

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
