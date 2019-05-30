#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`PackageMaker` class"""

from __future__ import absolute_import, print_function

import os
import string

from . import settings
from .base import BaseMaker


class PackageMaker(BaseMaker):
    """*Maker* class to create the package directory and main driver file for the package

    The name of the package directory is the same as the project name.
    However, the structure of package directory differs depending on the
    ``--format`` option.

    *skelpy* provides two kinds of package format: "basic" and "src".
    The directory trees below show the differences of the two formats ::

        basic format(default)                     src format

        my_project/                               my_project/
        └── my_project/                           └── src/
            ├── __init__.py                           └── my_project/
            └── main.py                                   ├── __init__.py
                                                          └── main.py

    Args:
        projectDir (str): absolute path of project's root directory
        projectName (str): project name
        format (str): type of package directory, i.e., basic or src
        merge (bool): whether to overlap package directory if the directory
            already exits
        force (bool): whether to overwrite if the file with the same name already exists
        kwargs : extra keyword arguments

    """
    def __init__(self, projectDir, projectName, format, merge, force, **kwargs):
        self.projectDir = projectDir
        self.projectName = projectName
        self.format = format
        self.merge = merge
        self.force = force
        if format == 'basic':
            self.packageDir = os.path.join(projectDir, projectName)
        else:
            self.packageDir = os.path.join(projectDir, 'src', projectName)

        self._update_settings()

    def _update_settings(self):
        """update :attr:`maker.settings` dictionary"""

        info = {
            'packageDir': self.packageDir,
        }

        settings.update(info)

    def _create_package_dir(self):
        """create package directory structure"""

        recursive = True if self.format == 'src' else False
        return self.create_dir(self.packageDir, recursive=recursive)

    def _write_init(self):
        """create __init__.py in the package directory"""

        content = ('# -*- coding: utf-8 -*-'
                   '\n'
                   '\n'
                   "__version__ = '${version}'"
                   '\n')
        intFile = os.path.join(self.packageDir, '__init__.py')
        return self.write_file(string.Template(content), intFile)

    def generate(self):
        """Worker method of :class:`PackageMaker`"""

        if not self._create_package_dir():
            return False

        self._write_init()
        self.write_file('main', os.path.join(self.packageDir, 'main.py'))
        return True
