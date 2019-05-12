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


@pytest.fixture(scope='module')
def setup_cfg():
    test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'test_data')
    src_file = os.path.join(test_data_dir, 'sample_setup.cfg')
    dest_file = os.path.join(gettempdir(), 'setup.cfg')
    shutil.copyfile(src_file, dest_file)
    yield dest_file
    # teardown
    os.remove(dest_file)


@pytest.fixture(scope='module')
def setup():
    templates_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     '..', 'skelpy', 'templates'))
    src_file = os.path.join(templates_dir, 'setup.tpl')
    dest_file = os.path.join(gettempdir(), 'setup.py')
    shutil.copyfile(src_file, dest_file)
    yield dest_file
    # teardown
    os.remove(dest_file)


@pytest.fixture(scope='module')
def changer():
    settings.clear()
    return license_change.Maker(list=False, license='NEW-BSD')


def test_update_settings(changer):
    assert settings.get('today') == datetime.date.today().isoformat()
    assert settings.get('projectName') == os.path.split(os.getcwd())[-1]


def test_replace_license(changer, setup_cfg, setup):
    # test setup.cfg
    conf_dict = read_setup_cfg(setup_cfg)
    assert conf_dict.get('license') == '${license}'
    changer.license = 'NEW-BSD'
    changer._replace_license(setup_cfg)
    conf_dict = read_setup_cfg(setup_cfg)
    assert conf_dict.get('license') == 'NEW-BSD'
    # test setup.py
    changer._replace_license(setup)
    with open(setup, 'rU') as f:
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

    with mock.patch('os.path.exists', return_value=False):
        changer.generate()

    assert os.path.exists(licFile)
    os.remove(licFile)
