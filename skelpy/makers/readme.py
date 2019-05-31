#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`ReadmeMaker` class."""

from __future__ import absolute_import, print_function

import os

from . import settings
from .base import BaseMaker


class ReadmeMaker(BaseMaker):
    """*Maker* class to create ``README.rst`` file in the project directory

    Args:
        projectDir (str): absolute path of the project directory
        projectName (str): project name
        kwargs: extra keyword arguments

    """
    def __init__(self, projectDir, projectName, force, **kwargs):
        self.projectDir = projectDir
        self.projectName = projectName
        self.force = force

        self._update_settings()

    def _update_settings(self):
        """update :attr:`maker.settings` dictionary"""

        info = {
            'line': '*' * len(self.projectName),
        }

        settings.update(info)

    def generate(self):
        """Worker method of :class:`ReadmeMaker`

        Returns:
            bool: True if successful, False otherwise

        """
        readmeFile = os.path.join(self.projectDir, 'README.rst')
        return bool(self.write_file('readme', readmeFile))
