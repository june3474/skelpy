#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_package - pytest module for PackageMaker

"""

from __future__ import absolute_import, print_function

import os
import pytest
from tempfile import gettempdir, tempdir

from skelpy.makers import base, package, settings
from . import mock


@pytest.fixture(scope='module')
def maker1():
    settings.clear()
    info = {
        'projectDir': gettempdir(),
        'projectName': 'project',
        'format': 'basic',
        'merge': False,
        'force': False,
    }
    return package.Maker(**info)


@pytest.fixture(scope='module')
def maker2():
    settings.clear()
    info = {
        'projectDir': gettempdir(),
        'projectName': 'project',
        'format': 'src',
        'merge': False,
        'force': False,
    }
    return package.Maker(**info)


def test_init(maker1, maker2):
    assert maker1.packageDir == os.path.join(gettempdir(), maker1.projectName)
    assert maker2.packageDir == os.path.join(gettempdir(), 'src', maker2.projectName)


def test_udpate_settings(maker1):
    maker1._update_settings()
    assert settings.get('packageDir') == os.path.join(maker1.projectDir,
                                                               maker1.projectName)


@mock.patch('os.makedirs')
@mock.patch('os.mkdir')
def test_create_package_dir(mocked_mkdir, mocked_makedirs, maker1, maker2):
    with mock.patch('os.path.exists', return_value=True):
        # merge == False && format == 'basic'
        assert maker1._create_package_dir() == 0
        mocked_mkdir.assert_not_called()
        mocked_makedirs.assert_not_called()
        # merge == True && format == 'basic'
        maker1.merge = True
        assert maker1._create_package_dir() == -1
        mocked_mkdir.assert_not_called()
        mocked_makedirs.assert_not_called()
        maker1.merge = False
    with mock.patch('os.path.exists', return_value=False):
        # merge == False && format == 'src'
        assert maker2._create_package_dir() == 1
        mocked_mkdir.assert_not_called()
        assert mocked_makedirs.called
        # merge == True && format == 'src'
        maker2.merge = True
        assert maker2._create_package_dir() == 1
        mocked_mkdir.assert_not_called()
        assert mocked_makedirs.called
        maker2.merge = False
        mocked_makedirs.call_count = 0


@mock.patch('os.fsync')
def test_write_init(mocked_fsync, maker1):
    with mock.patch.object(base, 'open', mock.mock_open(),
                           create=True) as mocked_open:
        with mock.patch('os.path.exists', return_value=True):
            # exist && force == False
            assert not maker1._write_init()
            mocked_open().write.assert_not_called()
            # exist && force == True
            maker1.force = True
            assert maker1._write_init()
            assert mocked_open().write.called
        with mock.patch('os.path.exists', return_value=False):
            # not exist
            assert maker1._write_init()
            content = ('# -*- coding: utf-8 -*-'
                       '\n'
                       '\n'
                       "__version__ = '${version}'"
                       '\n')
            mocked_open().write.assert_called_with(content)
