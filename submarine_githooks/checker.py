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
import functools
import os
import re
import six


class Checker(object):

    def __init__(self, callable_obj):
        self._callable = callable_obj
        functools.update_wrapper(self, self.callable)

        self.is_active_for_file = lambda x: True
        """:type: (str) -> bool"""
        self.active_hooks = []
        """:type: list[str]"""
        self.once = False

    def __call__(self, *args, **kwargs):
        self.callable(*args, **kwargs)

    def is_active_for_hook(self, hook_name):
        return not self.active_hooks or hook_name in self.active_hooks

    @property
    def name(self):
        return '{}.{}'.format(self.callable.__module__, self.callable.__name__)

    @property
    def callable(self):
        """
        :rtype: callable
        """
        return self._callable


class CheckerManager(object):

    def __call__(self, callable_obj):
        """
        :type callable_obj: callable | Checker
        :rtype: Checker
        """
        return self._get_or_create_checker(callable_obj)

    def file_pattern(self, regex):
        if isinstance(regex, six.string_types):
            regex = re.compile(regex)

        def wrapper(callable_or_checker_obj):
            checker_obj = self._get_or_create_checker(callable_or_checker_obj)
            checker_obj.is_active_for_file = lambda path: regex.search(path) is not None
            return checker_obj
        return wrapper

    def file_extension(self, file_ext):
        def wrapper(callable_or_checker_obj):
            checker_obj = self._get_or_create_checker(callable_or_checker_obj)
            checker_obj.is_active_for_file = lambda path: os.path.splitext(path)[-1] == file_ext
            return checker_obj
        return wrapper

    def file_name(self, *file_names):
        def wrapper(callable_or_checker_obj):
            checker_obj = self._get_or_create_checker(callable_or_checker_obj)
            checker_obj.is_active_for_file = lambda path: os.path.split(path)[-1] in file_names
            return checker_obj
        return wrapper

    def once(self, callable_or_checker_obj):
        checker_obj = self._get_or_create_checker(callable_or_checker_obj)
        checker_obj.once = True
        return checker_obj

    def file_validate(self, callable_obj):
        """
        :type callable_obj: (str) -> bool
        """
        def wrapper(callable_or_checker_obj):
            checker_obj = self._get_or_create_checker(callable_or_checker_obj)
            checker_obj.is_active_for_file = callable_obj
            return checker_obj
        return wrapper

    def active_hooks(self, *active_hook_names):
        def wrapper(callable_or_checker_obj):
            checker_obj = self._get_or_create_checker(callable_or_checker_obj)
            checker_obj.active_hooks += active_hook_names
            return checker_obj
        return wrapper

    @staticmethod
    def _get_or_create_checker(callable_or_checker_obj):
        """
        :type callable_or_checker_obj: callable | Checker
        :rtype: Checker
        """
        if isinstance(callable_or_checker_obj, Checker):
            return callable_or_checker_obj
        elif callable(callable_or_checker_obj):
            return Checker(callable_or_checker_obj)
        else:
            raise ValueError('{} object is neither a callable nor a Checker.'.format(callable_or_checker_obj))


checker = CheckerManager()
