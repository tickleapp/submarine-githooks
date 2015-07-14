#!/usr/bin/env python
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
from taskr import console
from taskr.contrib.git import GitRepo
from submarine_githooks.checker import Checker
from submarine_githooks.content import Content


# Get options and constants ============================================================================================
try:
    debug = int(os.environ.get('SUBMARINE_GITHOOK_DEBUG', '0')) != 0
except ValueError:
    debug = False
# Check for install test
install_test_str = os.environ.get('SUBMARINE_GITHOOK_INSTALL_TEST', None)
if install_test_str:
    print('submarine-githooks {}'.format(install_test_str))
    exit(0)

# from .git/hooks/pre-commit or etc
source_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
script_home = os.path.join(source_root, '.githooks')
git_repo = GitRepo(source_root)
# setup python path
sys.path.append(script_home)
# find hook name and python pacakges
hook_name = os.path.split(sys.argv[0])[-1]
checkers_package_dir = os.path.join(script_home, 'checkers')


# Find checkers ========================================================================================================
if debug:
    console.show('')
    console.info('Load checkers for {}'.format(hook_name), bar_width=120)
checkers = []
""":type: list[Checker]"""
for checker_path in os.listdir(checkers_package_dir):
    if checker_path.endswith('.py') and checker_path != '__init__.py':
        checker_module_str = 'checkers.' + os.path.splitext(checker_path)[0]
        checker_module = import_module(checker_module_str)
        for attr in dir(checker_module):
            checker = getattr(checker_module, attr)
            if isinstance(checker, Checker) and checker.is_active_for_hook(hook_name):
                checkers.append(checker)

if not checkers:
    if debug:
        console.warn('No checkers for {}'.format(hook_name))
    # sys.exit(0)
if debug:
    for checker in checkers:
        console.success('Found checker: {}'.format(checker.name))


# Find content to be checked ===========================================================================================
if debug:
    console.show('')
    console.info('Load contents for {}'.format(hook_name), bar_width=120)
contents = []
""":type: list[Content]"""
if hook_name == 'pre-commit':
    for git_file_path, (status_staged, status_working) in git_repo.status.items():
        full_file_path = os.path.join(git_repo.source_root, git_file_path)
        if status_staged in 'TMARC':
            content = Content.create_with_hook(hook_name,
                                               full_file_path, lambda f=git_file_path: git_repo.file_content(f))
            if content:
                contents.append(content)
elif hook_name == 'commit-msg':
    commit_message = sys.argv[-1]
    content = Content.create_with_hook(hook_name, commit_message)
    if content:
        contents.append(content)
elif hook_name == 'post-checkout':
    original_commit_id, destination_commit_id, branch_checkout = sys.argv[1:]
    branch_checkout = branch_checkout == '1'
    if branch_checkout:
        for changed_file in git_repo.changed_files(original_commit_id, destination_commit_id):
            full_file_path = os.path.join(git_repo.source_root, changed_file)
            content = Content.create_with_hook(hook_name,
                                               full_file_path, original_commit_id, destination_commit_id)
            if content:
                contents.append(content)
if not contents:
    if debug:
        console.warn('No content to check for {}'.format(hook_name))
    sys.exit(0)
if debug:
    for content in contents:
        console.success(content.discovered_message())


# Go, start to check ===================================================================================================
if debug:
    console.show('')
    console.info('Start check for {}'.format(hook_name), bar_width=120)
exit_code = 0
for content in contents:
    args = (git_repo,) + content.arguments
    for checker in checkers:
        if content.file_path and not checker.is_active_for_file(content.file_path):
            if debug:
                console.success(content.inactive_message(checker))
            continue
        # noinspection PyBroadException
        try:
            checker(*args)
        except Exception as e:
            console.show('')
            msg = '{} hook fails\nchecker: {}\n{}'.format(hook_name, checker.name, content.error_message(checker, e))
            console.error(msg)
            exit_code |= 1
        else:
            console.success(content.success_message(checker))

sys.exit(exit_code)
