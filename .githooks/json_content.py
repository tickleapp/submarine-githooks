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

import json
from submarine_githooks.checker import checker


# noinspection PyUnusedLocal
@checker
@checker.active_hooks('pre-commit')
@checker.file_extension('.json')
def pre_commit(git_repo, hook_name, file_path):
    """
    :param git_repo: a GitRepo instance representing current git repo
    :type git_repo: taskr.contrib.git.GitRepo
    :param hook_name: the hook being executing
    :type hook_name: str
    :param file_path: the path to of a file to be committed
    :type file_path: str
    """
    json.loads(git_repo.file_content(file_path))
