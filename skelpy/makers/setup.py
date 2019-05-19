#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`SetupMaker` class"""

from __future__ import absolute_import, print_function

import os
import sys
from functools import partial

from skelpy.utils.helpers import read_setup_cfg
from . import settings
from .base import BaseMaker


class SetupMaker(BaseMaker):
    """*Maker* class to create ``setup.py`` file in the project directory.

    Args:
        projectDir (str): absolute path of project directory
        force (bool): whether to overwrite if ``setup.py`` already exists

    """
    def __init__(self, projectDir, force, **kwargs):
        self.projectDir = projectDir
        self.force = force

        self._update_settings()

    def _update_settings(self):
        """update :attr:`maker.settings` dictionary"""

        settings.update(read_setup_cfg(os.path.join(self.projectDir, 'setup.cfg')))

        _format_multi_line_list = self._format
        _format_single_line_list = partial(self._format, indent=0, sep=', ')
        _format_multi_line_dict = partial(self._format, quote=False)

        info = {
            'exclude':
                _format_single_line_list(settings.get('exclude')),
            'python_requires':
                self._get_python_requires(settings.get('classifiers')),
            'classifiers':
                _format_multi_line_list(settings.get('classifiers')),
            'install_requires':
                _format_multi_line_list(settings.get('install_requires')),
            'setup_requires':
                _format_multi_line_list(settings.get('setup_requires')),
            'tests_require':
                _format_multi_line_list(settings.get('tests_require')),
            'extras_require':
                _format_multi_line_dict(settings.get('extras_require')),
        }

        settings.update(info)

    @staticmethod
    def _format(text, quote=True, indent=8, sep=',\n'):
        """ convert data read from setup.cfg to the suitable format for setup.py

        Args:
            text (str): string to format
            quote (bool): whether to surround the output string with quotation marks
            indent (int): indent spaces
            sep (str): line separator

        """
        if not text:
            return ''

        split_sep = '\n' if text.find('\n') != -1 else '; '

        if quote:
            opt_list = list(map(repr, text.split(split_sep)))
        else:
            opt_list = text.split(split_sep)

        INDENT = ' ' * indent
        separator = sep + INDENT
        return separator.join(opt_list)

    @staticmethod
    def _get_python_requires(classifiers):
        """Infer the required python version from the given classifiers string

        Args:
            classifiers (str): the value of 'classifiers' in settings

        Returns:
            str: minimum(lowest) python version required

        """
        count = 0
        min_ver = 'HIGH_VERSION'
        classifiers_list = classifiers.split('\n')
        for c in classifiers_list:
            if c.startswith('Programming Language :: Python'):
                count += 1
                ver = c.split('::')[-1].strip()
                if ver < min_ver:
                    min_ver = ver

        # if we can not determine the required_python_version, apply the current
        if min_ver == 'HIGH_VERSION':
            min_ver = sys.version.split()[0]

        sign = '>=' if count >= 2 else '=='

        return sign + min_ver

    def generate(self):
        """Worker method of :class:`SetupMaker`"""

        return self.write_file('setup',
                               os.path.join(self.projectDir, 'setup.py'))
