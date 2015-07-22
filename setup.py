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
import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as f:
    long_description = f.read()

setup(name='submarine-githooks',
      version='0.1.3',
      url='https://github.com/tickleapp/submarine-githooks',
      license='Apache License 2.0',
      author='sodas',
      author_email='sodas@tickleapp.com',
      description='Submarine Githooks',
      long_description=long_description,

      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'taskr>=0.2.28',
          'six>=1.8',
          'PyYAML>=3.0',
      ],

      entry_points={
          'console_scripts': [
              'submarine-githooks = submarine_githooks.main:task.dispatch',
              'submarine-githooks-entry = submarine_githooks.hooks:main',
          ],
      },

      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development',
          'Topic :: Utilities',
      ])
