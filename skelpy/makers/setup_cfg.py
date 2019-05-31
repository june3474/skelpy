#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`SetupCfgMaker` class."""

from __future__ import absolute_import, print_function

import os

from skelpy.utils import helpers
from . import settings
from .base import BaseMaker


class SetupCfgMaker(BaseMaker):
    """*Maker* class to creates ``setup.cfg`` in the project directory.

    Args:
        projectDir (str): absolute path of project directory to be created.
        projectName (str): project name
        format (str): package format. See :class:`PackageMaker`.
        force (bool): whether to overwrite if ``setup.cfg`` already exists
        test (str): testing tool to use. i.e., ``unittest`` or ``pytest``
            See :class:`TestMaker`.

    """

    def __init__(self, projectDir, projectName, format, quiet, force, test, **kwargs):
        self.projectDir = projectDir
        self.projectName = projectName
        self.format = format
        self.quiet = quiet
        self.force = force
        self.test = test

        self._update_settings()

    def _update_settings(self):
        """update :attr:`maker.settings` dictionary"""

        info = {
            'package_dir': '.' if self.format == 'basic' else 'src',
            'pytest': 'pytest' if self.test == 'pytest' else '',
            'pytest_runner': 'pytest-runner' if self.test == 'pytest' else '',
            'pytest_alias': 'test = pytest\n' if self.test == 'pytest' else '',
            'python_version': helpers.get_python_version(),
            'python_version_short': helpers.get_python_version(short=True),
        }

        settings.update(info)

    def generate(self):
        """Worker method of :class:`SetupCfgMaker`"""

        return self.write_file('setup_cfg',
                               os.path.join(self.projectDir, 'setup.cfg'))
