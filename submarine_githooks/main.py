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
import datetime
from taskr import task, console
from taskr.contrib.system import run as taskr_run
from taskr.contrib.validators import validate_boolean
from submarine_githooks.checker import Checker
from submarine_githooks.constants import hook_names

source_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@task
def install(dry_run=False, verbose=False):
    git_path = '.git'
    git_hooks_path = os.path.join(git_path, 'hooks')
    script_home = '.githooks'
    checkers_home = script_home
    entry_command_path, _ = taskr_run('which submarine-githooks-entry')

    assert entry_command_path, 'Cannot find the location of `submarine-githooks-entry`'
    assert os.path.exists(git_path), 'Cannot find `.git` folder at current working directory.'

    def run(command):
        if dry_run:
            print(command)
        else:
            taskr_run(command, print_command=verbose, capture_output=False)

    # Create hooks
    hook_link_commands = []
    for hook_name in hook_names:
        target_hook_path = '{git_hooks_path}/{hook_name}'.format(**locals())
        if os.path.abspath(os.path.realpath(target_hook_path)) != os.path.abspath(entry_command_path):
            if os.path.exists(target_hook_path):
                hook_link_commands.append('mv {target_hook_path} {target_hook_path}-{timestamp}'.format(
                    timestamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S'),
                    **locals())
                )
            hook_link_commands.append('ln -s {entry_command_path} {git_hooks_path}/{hook_name}'.format(**locals()))

    if hook_link_commands:
        run('mkdir -p {git_hooks_path}'.format(**locals()))
        for hook_link_command in hook_link_commands:
            run(hook_link_command)

    # Create checkers room
    if not os.path.exists(checkers_home):
        run('mkdir -p {checkers_home}'.format(**locals()))
    if not os.path.exists('{checkers_home}/__init__.py'.format(**locals())):
        run('touch {checkers_home}/__init__.py'.format(**locals()))


@task
def setup_script(dest_path='.', script_name='setup-githooks'):
    content = '''#!/bin/sh

# Check Python dependency
python -c "import submarine_githooks" 1>/dev/null 2>&1 || pip install -U submarine-githooks
# Setup
submarine-githooks install
'''
    dest_path = os.path.abspath(os.path.join(dest_path, script_name))

    with open(dest_path, 'w') as f:
        f.write(content)
    taskr_run('chmod +x {dest_path}'.format(**locals()))


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
    dest_checkers_path = '.githooks'
    if not os.path.exists(dest_checkers_path):
        raise IOError('No such directory: {}'.format(dest_checkers_path))

    src_checker_module_path = os.path.join(source_root, *checker_module_str.split('.')) + '.py'
    dest_checker_module_path = os.path.join(dest_checkers_path, os.path.split(src_checker_module_path)[-1])
    if (not os.path.exists(dest_checker_module_path) or
            console.input('File exists. Overwrite?', default='N', hint='y/n', validators=[validate_boolean])):
        taskr_run('cp {} {}'.format(src_checker_module_path, dest_checker_module_path))


if __name__ == '__main__':
    task.dispatch()
