#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`LicenseChanger` class."""

from __future__ import absolute_import, print_function

import os

from skelpy.utils.helpers import read_setup_cfg, get_userName
from . import settings
from .license import LicenseMaker


class LicenseChanger(LicenseMaker):
    """*Maker* class to change the existing ``LICENSE`` file

    As of now, LicenseMaker changes ``LICENSE`` file in the **current**
    **directory**, i.e., in the directory where skelpy is executed or ``os.getcwd()``:

        * ``LICENSE``
        * ``setup.cfg``
        * ``setup.py``

    Todo:
        * enable to change the license in other directory(project)

    Args:
        list (bool): if True, print the list of supported licenses without changing
            (default: False)
        license (str): license to change to

    """
    def __init__(self, list_option, license=LicenseMaker.default_license):
        self.list_option = list_option
        self.license = license.upper()
        self.projectDir = os.getcwd()
        self.force = True
        self.quiet = True

        self._update_settings()

    def _update_settings(self):
        """update :attr:`maker.settings` dictionary"""

        super(LicenseChanger, self)._update_settings()
        if not settings.get('author'):
            settings['author'] = get_userName()
        # set the current directory to the project name
        if not settings.get('projectName'):
            settings['projectName'] = os.path.split(os.getcwd())[-1]

    def _replace_license(self, file):
        """replace license type in contents of the given file

        Args:
            file: file to change the license type

        Returns:
            bool: True if successful, False otherwise

        """
        import re

        lic_expr = re.compile(r'''(license\s*=\s*)(['"]?)[${}\-\w]+(['"]?)''')

        try:
            with open(file, 'r') as f:
                content = f.read()
        except Exception:
            return False

        try:
            with open(file, 'wt') as f:
                f.write(re.sub(lic_expr, r'\1\2{}\3'.format(self.license), content))
        except Exception:
            return False

        return True

    def generate(self):
        """Worker method of :class:`LicenseChanger`

        This method changes not only the ``LICENSE`` file under the project
        directory but also the license attribute in the setup.py and the
        setup.cfg accordingly if they exist.

        Returns:
            bool: True if successful, otherwise False

        """
        #: check --list option first
        if self.list_option:
            self.print_licenses()
            return True

        if not self.is_supported_license(self.license):
            self.logger.error(
                "unsupported license: '{}'".format(self.license))
            self.print_licenses()
            return False

        #: modify setup.cfg if exists
        cfgFile = os.path.join(self.projectDir, 'setup.cfg')
        if os.path.exists(cfgFile):
            self._replace_license(cfgFile)
            self.logger.info("modified 'setup.cfg'")
            settings.update(read_setup_cfg(cfgFile))

        #: modify setup.py if exists
        setupFile = os.path.join(self.projectDir, 'setup.py')
        if os.path.exists(setupFile):
            self._replace_license(setupFile)
            self.logger.info("modified 'setup.py'")

        # change LICENSE
        return super(LicenseChanger, self).generate()
