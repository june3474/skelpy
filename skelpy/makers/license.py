#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`LicenseMaker` class."""

from __future__ import absolute_import, print_function

import os
import datetime

from . import settings
from .base import BaseMaker


#: Supported licenses, corresponding template file names, and descriptions
_LICENSES = {
    "APACHE": ["license_apache", "Apache License"],
    "CC0": ["license_cc0_1.0", "Creative Commons License for public domain"],
    "GPL2": ["license_gpl_2.0", "GNU General Public License v2.0"],
    "GPL3": ["license_gpl_3.0", "GNU General Public License v3.0"],
    "LGPL2": ["license_lgpl_2.1", "GNU Lesser General Public License v2.1"],
    "LGPL3": ["license_lgpl_3.0", "GNU Lesser General Public License v3.0"],
    "MIT": ["license_mit", "MIT License, Default"],
    "MOZILLA": ["license_mozilla", "Mozilla Public License v2.0"],
    "NEW-BSD": ["license_new_bsd", "New BSD(Berkeley Software Distribution) License"],
    "SIMPLE-BSD": ["license_simplified_bsd", "Simplified BSD(Berkeley Software Distribution) License"],
    "PROPRIETARY": ["license_proprietary", "Proprietary License"],
}


class LicenseMaker(BaseMaker):
    """*Maker* class to create ``LICENSE`` file in the project directory

    ``LicenseMaker`` basically choose the license specified in setup.cfg file.
    But if it can not retrieve a license from the file--for
    example, when the user did not specify a license in setup.cfg-- it creates
    the default license, which is the `MIT license <https://opensource.org/licenses/MIT>`_.

    Args:
        projectDir (str): absolute path of project directory to create
        force (bool): option for overwriting  if the file exists.
        license (str): license to create.

    Attributes:
        default_license (str): default license(class variable)

    """
    default_license = 'MIT'

    def __init__(self, projectDir, force, license, **kwargs):
        self.projectDir = projectDir
        self.force = force
        self.license = license

        self._update_settings()

    def _update_settings(self):
        """update :attr:`maker.settings` dictionary"""

        info = {
            'today': datetime.date.today().isoformat(),
            'year': str(datetime.date.today().year),
        }

        settings.update(info)

    @staticmethod
    def is_supported_license(license):
        """check to see if the license given is supported by *skelpy* or not

        license name is case-insensitive.

        .. Note::

             Currently supported licenses are::

                 * APACHE: Apace License
                 * CC0: Creative Commons License for public domain
                 * GPL2: GNU General Public License v2.0
                 * GPL3: GNU General Public License v3.0
                 * LGPL: GNU Lesser General Public License v2.1
                 * LGPL3: GNU Lesser General Public License v3.0
                 * MIT: MIT License, **Default**
                 * MOZILLA: Mozilla Public License v2.0
                 * NEW-BSD: New BSD(Berkeley Software Distribution) License
                 * SIMPLE-BSD: Simplified BSD License
                 * PROPRIETARY: Proprietary License

        Args:
            license (str): license name

        Returns:
            bool: True if the license given is supported, False otherwise

        """
        return bool(_LICENSES.get(license.upper()))

    @staticmethod
    def print_licenses():
        """print supported licenses

        Returns:
            None

        """
        print('Supported licenses are as follows:')
        indent = " " * 4
        for k, v in _LICENSES.items():
            print('{0}{1}: {2}'.format(indent, k, v[1]))

    def generate(self):
        """Worker method of :class:`LicenseMaker`

        Returns:
            bool: True if successful, False otherwise

        """
        licFile = os.path.join(self.projectDir, 'LICENSE')

        ret = self.write_file(_LICENSES[self.license][0], licFile)
        if not ret:
            self.logger.info(
                "* You can change the license with 'license' sub-command.\n"
                "For help, see 'skelpy license -h or --help'.")

        return bool(ret)
