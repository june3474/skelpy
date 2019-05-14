#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`ProjectMaker` class.

"""

from __future__ import absolute_import, print_function

import os
from tempfile import gettempdir

from utils import opener, helpers
from . import get_maker, settings
from .base import BaseMaker
from .license import LicenseMaker


class ProjectMaker(BaseMaker):
    """*Maker* class to create the project directory

    After creating the project directory, ``ProjectMaker`` creates several
    configuration files in the directory using the appropriate *Maker*.
    Below are the configuration files to be created::

        * setup.py
        * setup.cfg
        * LICENSE
        * README.rst
        * .gitignore

    Args:
        projectName (str): project name, in effect, the directory to create.
        projectDir (str): absolute path of project directory to be created.

            .. note::
               projectDir should include the *projectName* as its last component.
               In other words, the following statement must be True.

                   ``os.path.split(projectDir)[-1] == projectName``

        merge (bool): whether to overlap the project directory if the directory
            already exists
        force (bool): whether to overwrite if the file with the same name already exists

    """

    def __init__(self, projectDir, projectName, quiet, merge, force, **kwargs):
        self.projectDir = projectDir
        self.projectName = projectName
        self.quiet = quiet
        self.merge = merge
        self.force = force

        self.default_license = 'MIT'
        self._update_info()

    def _update_info(self):
        """update :attr:`maker.settings` dictionary"""

        defaults = {
            'author': helpers.get_userName(),
            'author_email': helpers.get_email(),
            'version': '1.0.0',
            'license': self.default_license,
            'description': 'ADD SHORT DESCRIPTION ON THE PROJECT HERE'}

        settings.update(defaults)

    def _get_info(self):
        """collect project information from the user

        This private method opens the default text editor and
        get the user input on the project such as license,
        short description of the project.
        Collected information is used to create setup.py and setup.cfg.

        Returns:
            bool: True if successful, False otherwise

        """
        if self.quiet:
            return

        try:
            from configparser import ConfigParser  # python3
        except ImportError:
            from ConfigParser import ConfigParser  # python2

        infoFile = os.path.join(gettempdir(), 'info.txt')
        if not self.write_file('info', infoFile):
            return False

        if opener.open_with_associated_application(infoFile, block=True) == -1:
            return False

        parser = ConfigParser()
        try:
            with open(infoFile, 'rU') as f:
                parser.readfp(f)
        except Exception:
            return False

        os.remove(infoFile)
        for section in parser.sections():
            settings.update(parser.items(section))

        return True

    def _check_license(self):
        """check if the license is valid.

        If the license is invalid or unsupported
        the default license(MIT) is used instead.

        """
        license = settings.get('license')
        #LicenseMaker = get_maker('license')

        if not LicenseMaker.is_supported_license(license):
            self.logger.info(
                "Invalid license: '{}'\n".format(license)
                + "default '{}' license will be used.\n".format(self.default_license)
                + "* You can change the license later with 'license' sub-command.\n"
                + "For help, see 'skelpy license -h/--help'.")
            settings['license'] = self.default_license
        else:
            settings['license'] = license.upper()

    def _create_config_files(self):
        """create configuration files

        Returns:
            bool: True if successful, False otherwise
        """

        makers = ['setup_cfg',
                  'setup',
                  'license',
                  'readme']

        for m in makers:
            maker_cls = get_maker(m)
            if not maker_cls:
                self.logger.warning(
                    "module not found: '{}'".format(m + '.py')
                    + '   skipping...')
                continue

            maker = maker_cls(**settings)
            if not maker.generate():
                return False

        return True

    def _create_miscellaneous(self):
        """create other miscellaneous configuration files

        Currently, this method only creates .gitignore when it detects
        `git <https://git-scm.com/>`_ is installed. You can extend this method
         to create other files by adding a couple of codes as shown in the
         example below.

        Example:
            Add `.editorconfig <https://editorconfig.org/>`_ provided that
            .editorconfig.tpl is in the templates directory::

                if not self.write_file('.editorconfig',
                                       os.path.join(self.projectDir, '.editorconfig')):
                    return False

        Returns:
            bool: True if successful, False otherwise

        """

        # .gitignore
        if helpers.has_command('git'):
            if not self.write_file('.gitignore',
                                   os.path.join(self.projectDir, '.gitignore')):
                return False

        return True

    def generate(self):
        """Worker method of :class:`ProjectMaker`

        Returns:
            bool: True if successful, False otherwise

        """
        if not self.create_dir(self.projectDir, recursive=True):
            return False

        if not self._get_info():
            return False

        self._check_license()

        if not self._create_config_files():
            return False

        if not self._create_miscellaneous():
            return False

        return True
