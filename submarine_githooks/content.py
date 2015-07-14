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

    def __init__(self, *args):
        self._arguments = args

    @staticmethod
    def create_with_hook(hook_name, *args):
        """
        :type hook_name: str
        :rtype: Content
        """
        klass = None
        if hook_name in ('pre-commit', 'post-checkout', 'post-merge', 'commit-msg'):
            klass = FilePathContent
        elif hook_name == 'pre-push':
            klass = PrePushContent

        # noinspection PyCallingNonCallable
        return klass(*args) if klass else None

    @property
    def arguments(self):
        return self._arguments

    @property
    def file_path(self):
        """
        :rype: str | None
        """
        return None

    # Messages

    def discovered_message(self):
        """
        :rtype: str
        """
        return ''

    def inactive_message(self, checker):
        """
        :type checker: aquarium_githooks.checker.Checker
        :rtype: str
        """
        # noinspection PyTypeChecker
        return ''

    def error_message(self, checker, exception):
        """
        :type checker: aquarium_githooks.checker.Checker
        :type exception: Exception
        :rtype: str
        """
        return str(exception)

    def success_message(self, checker):
        """
        :type checker: aquarium_githooks.checker.Checker
        :rtype: str
        """
        return ''


class FilePathContent(Content):

    @property
    def file_path(self):
        """
        :rype: str | None
        """
        return self._arguments[0]

    @property
    def rel_file_path(self):
        return os.path.relpath(self.file_path)

    def discovered_message(self):
        """
        :rtype: str
        """
        # noinspection PyTypeChecker
        return 'Found content: {}'.format(self.rel_file_path)

    def inactive_message(self, checker):
        """
        :type checker: aquarium_githooks.checker.Checker
        :rtype: str
        """
        # noinspection PyTypeChecker
        return '"{}" is inactive for "{}"'.format(checker.name, self.rel_file_path)

    def error_message(self, checker, exception):
        """
        :type checker: aquarium_githooks.checker.Checker
        :type exception: Exception
        :rtype: str
        """
        # noinspection PyTypeChecker
        return 'file: {}\n{}'.format(self.rel_file_path,
                                     super(FilePathContent, self).error_message(checker, exception))

    def success_message(self, checker):
        """
        :type checker: aquarium_githooks.checker.Checker
        :rtype: str
        """
        return 'Invoked "{}" with "{}" successfully'.format(checker.name, self.rel_file_path)


class PrePushContent(Content):

    def discovered_message(self):
        """
        :rtype: str
        """
        return 'Found push action to {} ({})'.format(self.arguments[0], self.arguments[1])

    def inactive_message(self, checker):
        """
        :type checker: aquarium_githooks.checker.Checker
        :rtype: str
        """
        # noinspection PyTypeChecker
        return '"{}" is not active to push action'.format(checker.name)

    def success_message(self, checker):
        """
        :type checker: aquarium_githooks.checker.Checker
        :rtype: str
        """
        return 'Invoked "{}" with push information'.format(checker.name)
