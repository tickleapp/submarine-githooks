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
from taskr import task
from taskr.contrib.system import run as taskr_run
from submarine_githooks.checker import Checker

source_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

hook_names = (
    'applypatch-msg',
    'pre-applypatch',
    'post-applypatch',
    'pre-commit',
    'prepare-commit-msg',
    'commit-msg',
    'post-commit',
    'pre-rebase',
    'post-checkout',
    'post-merge',
    'pre-auto-gc',
    'post-rewrite',
    'pre-push',
)


@task
@task.set_argument('-d', '--dry-run', action='store_true')
def install(dry_run=False):
    git_path = '.git'
    script_home = '.githooks'
    entry_script_dir = os.path.join(script_home, 'entry')
    entry_script_filename = 'entry.py'
    entry_script_path = os.path.join(script_home, entry_script_filename)
    entry_script_src_path = os.path.join(source_root, 'hooks.py')
    checkers_path = os.path.join(script_home, 'checkers')

    assert os.path.exists(git_path), 'Cannot find `.git` folder at current working directory.'

    def run(command):
        if dry_run:
            print(command)
        else:
            taskr_run(command)

    git_hook_path = os.path.join(git_path, 'hooks')
    backup_git_hook_path = os.path.join(git_path, 'hooks.original')

    # Check whether setup is ready or not
    if not dry_run:
        stdout, _ = taskr_run('SUBMARINE_GITHOOK_INSTALL_TEST=1 {entry_script_path}'.format(**locals()),
                              use_shell=True)
        if stdout == 'submarine-githooks 1':
            return  # Installed

    # Move current git hooks as backup
    run('mv {git_hook_path} {backup_git_hook_path}'.format(**locals()))
    # Create links from .git/hooks to .aquarium_githooks/hooks
    run('ln -s ../{entry_script_dir} {git_hook_path}'.format(**locals()))
    # Create folder for aquarium-githooks
    run('mkdir -p {entry_script_dir}'.format(**locals()))
    # Create hooks
    for hook_name in hook_names:
        run('ln -s ../{entry_script_filename} {entry_script_dir}/{hook_name}'.format(**locals()))
    # Setup script
    run('cp {entry_script_src_path} {entry_script_path}'.format(**locals()))
    run('chmod +x {entry_script_path}'.format(**locals()))
    # Create checkers room
    run('mkdir -p {checkers_path}'.format(**locals()))
    run('touch {checkers_path}/__init__.py'.format(**locals()))


@task
def setup_script(dest_path='.'):
    file_name = 'setup-githooks'
    source_path = os.path.join(source_root, file_name)
    dest_path = os.path.abspath(os.path.join(dest_path, file_name))
    taskr_run('mv {source_path} {dest_path} && chmod +x {dest_path}'.format(
        source_path=source_path, dest_path=dest_path))


@task
def vendored_checkers():
    checker_modules = []
    checkers_package = 'submarine_githooks.contrib.checkers'
    checkers_package_path = os.path.join(source_root, 'submarine_githooks', 'contrib', 'checkers')
    for module_file in os.listdir(checkers_package_path):
        if os.path.splitext(module_file)[-1] == '.py' and module_file != '__init__.py':
            checker_module_str = '{}.{}'.format(checkers_package, os.path.splitext(module_file)[0])
            checker_module = import_module(checker_module_str)
            for attr in dir(checker_module):
                if isinstance(getattr(checker_module, attr), Checker):
                    checker_modules.append(checker_module_str)

    for checker_module in checker_modules:
        print(checker_module)


@task
def install_checker(checker_module_str):
    checker_module_path = os.path.join(source_root, *checker_module_str.split('.')) + '.py'
    taskr_run('mv {} .githooks/checkers/{}'.format(checker_module_path, os.path.split(checker_module_path)[-1]))


if __name__ == '__main__':
    task.dispatch()
