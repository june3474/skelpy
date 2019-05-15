#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_test - pytest module for TestMaker

"""

from __future__ import absolute_import, print_function

import os
import pytest
from tempfile import gettempdir, tempdir

from skelpy.makers import tests, settings
from . import mock


@pytest.fixture(scope='module')
def maker():
    settings.clear()
    opts = {
        'projectDir': gettempdir(),
        'force': True,
        'merge': False,
        'test': 'unittest'
    }
    return tests.TestMaker(**opts)


def test_update_settings(maker):
    assert settings['testsDir'] == os.path.join(maker.projectDir, 'tests')

def test_create_config_files(maker):
    with mock.patch.object(maker, 'write_file') as mocked_write:
        mocked_write.reset_mock()
        maker._create_config_files()
        mocked_write.assert_called_with('test_init',
                                        os.path.join(maker.testsDir, '__init__.py'))
        mocked_write.assert_any_call('test_main_unittest',
                                     os.path.join(maker.testsDir, 'test_main.py'))

        mocked_write.reset_mock()
        maker.test = 'pytest'
        maker._create_config_files()
        mocked_write.assert_any_call('test_main_pytest',
                                     os.path.join(maker.testsDir, 'test_main.py'))


@mock.patch('os.mkdir')
def test_generate(mocked_mkdir, maker):
    with mock.patch.object(maker, 'write_file') as mocked_write:
        # test create_dir part
        # dir exist
        with mock.patch('os.path.exists', return_value=True):
            # exist & not merge
            maker.merge = False
            maker.generate()
            mocked_mkdir.assert_not_called()
            mocked_write.assert_not_called()
            # exist & merge
            maker.merge = True
            maker.generate()
            mocked_mkdir.assert_not_called()
            assert mocked_write.called

        # not exist
        with mock.patch('os.path.exists', return_value=False):
            maker.merge = False
            maker.generate()
            mocked_mkdir.assert_any_call(maker.testsDir, 0o755)
