#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`DocMaker` class"""

from __future__ import absolute_import, print_function

import os

from . import settings
from .base import BaseMaker


class DocMaker(BaseMaker):
    """*Maker* class to create directories and configuration files for documentation

    ``DocMaker`` creates a directory named "*docs*" under the project's root directory.
    Below is the structure of the *docs* directory to be created::

        project
        └── docs
            ├── _build
            ├── _static
            ├── _templates
            ├── conf.py
            ├── index.rst
            ├── make.bat
            └── Makefile

    Args:
        projectDir (str): path of the project directory
        merge (bool): Whether to overlap docs directory if the directory
            already exists
        force (bool): whether to overwrite if the file with the same name already exists
        kwargs: extra keyword arguments

    """

    def __init__(self, projectDir, merge, force, **kwargs):
        self.projectDir = projectDir
        self.docsDir = os.path.join(projectDir, 'docs')
        self.merge = merge
        self.force = force
        self.TITLE_SUFFIX = " Documentation"

        self._update_settings()

    def _update_settings(self):
        """update :attr:`maker.settings` dictionary"""

        doc_title = settings.get('projectName') + self.TITLE_SUFFIX
        info = {
            'docsDir': self.docsDir,
            'doc_title': doc_title,
            'doc_title_line': '*' * len(doc_title),
        }

        settings.update(info)

    def _create_dirs(self):
        """create sub-directories"""

        dirs = [self.docsDir,
                os.path.join(self.docsDir, '_build'),
                os.path.join(self.docsDir, '_static'),
                os.path.join(self.docsDir, '_templates')]

        for d in dirs:
            if not self.create_dir(d):
                return False

        return True

    def _create_config_files(self):
        """create general configuration files"""

        config_files = {
            'sphinx_conf': 'conf.py',
            'sphinx_index': 'index.rst',
            'Makefile': 'Makefile',
            'make_bat': 'make.bat',
        }

        for tpl, target in config_files.items():
            config_file = os.path.join(self.docsDir, target)
            if not self.write_file(tpl, config_file):
                return False

        return True

    def generate(self):
        """Worker method of :class:`DocMaker`

        Returns:
            bool: True if successful, False otherwise

        """

        if not self._create_dirs():
            return False

        return self._create_config_files()
