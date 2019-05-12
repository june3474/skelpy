#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_project - pytest module for ProjectMaker

"""

from __future__ import absolute_import, print_function

import os
import pytest

from tempfile import gettempdir, tempdir

from . import mock
from skelpy.makers import project, settings


@pytest.fixture()
def maker():
    settings.clear()
    opts = {
        'projectDir': gettempdir(),
        'projectName': 'project',
        'format': 'basic',
        'quiet': False,
        'merge': False,
        'force': True,
        'verbose': True,
        'test': 'pytest',
    }
    settings.update(opts)
    return project.Maker(**opts)


def test_get_info(maker):
    maker._get_info()
    # assert Not None
    assert settings.get('license')
    assert settings.get('description')


def test_check_license(maker):
    with mock.patch.object(maker.logger, 'info') as mocked_info:
        with mock.patch.dict(settings, {'license': 'INVALID'}):
            maker._check_license()
            assert mocked_info.called
            assert settings.get('license') == 'MIT'
        with mock.patch.dict(settings, {'license': 'new-bsd'}):
            maker._check_license()
            assert mocked_info.not_called
            assert settings.get('license') == 'NEW-BSD'


def test_create_config_files(maker):
    cfgFile = os.path.join(maker.projectDir, 'setup.cfg')
    setupFile = os.path.join(maker.projectDir, 'setup.py')
    licFile = os.path.join(maker.projectDir, 'LICENSE')
    readmeFile = os.path.join(maker.projectDir, 'README.rst')
    files = [cfgFile, setupFile, licFile, readmeFile]

    maker._create_config_files()
    for f in files:
        assert os.path.exists(f)
        os.remove(f)


def test_create_miscellaneous(maker):
    mocked_write = mock.Mock()
    maker.write_file = mocked_write
    # check .gitignore
    gitignore = os.path.join(tempdir, '.gitignore')
    with mock.patch.object(project.helpers, 'has_command', side_effect=[True, False]):
        maker._create_miscellaneous()
        assert mocked_write.called is True
        assert mocked_write.call_args == ((mock.ANY, gitignore),)
        maker._create_miscellaneous()
        assert mocked_write.assert_not_called
