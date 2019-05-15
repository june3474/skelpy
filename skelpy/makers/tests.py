#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`TestMaker` class"""

from __future__ import absolute_import, print_function

import os

from . import settings
from .base import BaseMaker


class TestMaker(BaseMaker):
    """*Maker* class to create directories and configuration files for testing

    TestMaker creates a directory named ``tests`` and ``test_main.py`` file in that directory.

    Args:
        projectDir (str): absolute path of project directory
        force (bool): whether to overwrite if *test_main.py* already exists
        test (str): testing tool to use. *skelpy* supports two testing
            tools: :mod:`unittest` and `pytest(default)  <https://pytest.org/>`_

    """

    def __init__(self, projectDir, merge, force, test, **kwargs):
        self.projectDir = projectDir
        self.testsDir = os.path.join(self.projectDir, 'tests')
        self.merge = merge
        self.force = force
        self.test = test

        self._update_settings()

    def _update_settings(self):
        """update :attr:`maker.settings` dictionary"""

        info = {
            'testsDir': self.testsDir,
        }

        settings.update(info)

    def _create_config_files(self):
        """create general configuration files"""

        if not self.write_file('test_main_' + self.test,
                               os.path.join(self.testsDir, 'test_main.py')):
            return False

        if not self.write_file('test_init',
                               os.path.join(self.testsDir, '__init__.py')):
            return False

        return True

    def generate(self):
        """Worker method of :class:`TestMaker`"""

        if not self.create_dir(self.testsDir):
            return False

        if not self._create_config_files():
            return False

        return True
