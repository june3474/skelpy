#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pytest_module for LicenseChanger"""

from __future__ import absolute_import, print_function

import os
import pytest
import shutil
import datetime
from tempfile import gettempdir

from skelpy.makers import license_change, settings
from skelpy.utils.helpers import read_setup_cfg
from . import mock

skelpy_projDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..' ))


@pytest.fixture(scope='module')
def setup_cfg():
    src_file = os.path.join(skelpy_projDir, 'setup.cfg')
    dest_file = os.path.join(gettempdir(), 'setup.cfg')
    shutil.copyfile(src_file, dest_file)
    yield dest_file
    # teardown
    os.remove(dest_file)


@pytest.fixture(scope='module')
def setup():
    src_file = os.path.join(skelpy_projDir, 'setup.py')
    dest_file = os.path.join(gettempdir(), 'setup.py')
    shutil.copyfile(src_file, dest_file)
    yield dest_file
    # teardown
    os.remove(dest_file)


@pytest.fixture(scope='module')
def changer(setup, setup_cfg):
    os.chdir(gettempdir())

    settings.clear()
    return license_change.Maker(list_option=False, license='NEW-BSD')


def test_update_settings(changer):
    # 'today' is set in the parent class, i.e., LicenseMaker
    assert settings.get('today') == datetime.date.today().isoformat()
    assert settings.get('projectName') == os.path.split(os.getcwd())[-1]


def test_replace_license(changer):
    # test setup.cfg
    conf_dict = read_setup_cfg('setup.cfg')
    assert conf_dict.get('license') == 'MIT'
    changer.license = 'NEW-BSD'
    changer._replace_license('setup.cfg')
    conf_dict = read_setup_cfg('setup.cfg')
    assert conf_dict.get('license') == 'NEW-BSD'
    # test setup.py
    changer._replace_license('setup.py')
    with open('setup.py', 'r') as f:
        content = f.read()
    assert "license='NEW-BSD'" in content


def test_generate(changer):
    with mock.patch.object(changer, 'print_licenses') as mocked_print:
        # list_option option given
        changer.list = True
        changer.generate()
        assert mocked_print.call
        # invalid license
        with mock.patch('os.path.join') as mocked_join:
            changer.license = 'INVALID'
            changer.generate()
            assert mocked_print.call
            mocked_join.assert_not_called()

    changer.projectDir = gettempdir()
    changer.license = 'NEW-BSD'
    changer.list = False
    licFile = os.path.join(changer.projectDir, 'LICENSE')
    if os.path.exists(licFile):
        os.remove(licFile)

    # don't mess with setup.py & setup.cfg tested above already
    with mock.patch('os.path.exists', return_value=False):
        changer.generate()

    assert os.path.exists(licFile)
    os.remove(licFile)
