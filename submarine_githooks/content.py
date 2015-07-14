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
import os


class Content(object):

    def __init__(self):
        self._arguments = ()
        self._hook_name = None

    @staticmethod
    def create_with_hook(hook_name, *args):
        """
        :type hook_name: str
        :rtype: Content
        """
        klass = None
        if hook_name == 'pre-commit':
            klass = PreCommitContent

        # noinspection PyCallingNonCallable
        return klass(*args) if klass else None

    @property
    def arguments(self):
        return self._arguments

    @property
    def hook_name(self):
        return self._hook_name

    @property
    def file_path(self):
        """
        :rype: str | None
        """
        return self._arguments[0]

    # Messages

    def discovered_message(self):
        """
        :rtype: str
        """
        # noinspection PyTypeChecker
        return 'Found content: {}'.format(os.path.relpath(self.file_path)) if self.file_path else ''

    def inactive_message(self, checker):
        """
        :type checker: aquarium_githooks.checker.Checker
        :rtype: str
        """
        # noinspection PyTypeChecker
        return '"{}" is inactive for "{}"'.format(checker.name, os.path.relpath(self.file_path)) \
            if self.file_path else ''

    def error_message(self, checker, exception):
        """
        :type checker: aquarium_githooks.checker.Checker
        :type exception: Exception
        :rtype: str
        """
        # noinspection PyTypeChecker
        return '{} hook fails\nchecker: {}\nfile: {}\n{}'\
            .format(self.hook_name, checker.name, os.path.relpath(self.file_path), str(exception))\
            if self.file_path else ''

    def success_message(self, checker):
        """
        :type checker: aquarium_githooks.checker.Checker
        :rtype: str
        """
        return 'Invoked "{}" with "{}" successfully'.format(checker.name, self.file_path) if self.file_path else ''


class PreCommitContent(Content):

    def __init__(self, file_path, content_loader):
        super(PreCommitContent, self).__init__()
        self._arguments = (file_path, content_loader)
        self._hook_name = 'pre-commit'
