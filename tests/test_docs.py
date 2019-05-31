#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_package - pytest module for DocMaker

"""

from __future__ import absolute_import, print_function

import os
import pytest
from tempfile import gettempdir

from skelpy.makers import base, docs, settings
from . import mock


@pytest.fixture(scope='module')
def maker():
    settings.clear()
    info = {
        'projectDir': gettempdir(),
        'projectName': 'project',
        'merge': False,
        'force': False,
    }
    settings['projectName'] = 'project'
    return docs.Maker(**info)


def test_update_settings(maker):
    maker._update_settings()
    assert settings.get('docsDir') == os.path.join(maker.projectDir, 'docs')
    assert settings.get('doc_title') == "project Documentation"


@mock.patch('os.mkdir')
@mock.patch('sys.exit')
def test_create_dirs(mocked_exit, mocked_mkdir, maker):
    #: dirs exist
    with mock.patch('os.path.exists', return_value=True):
        # exist & not merge
        maker.merge = False
        assert maker._create_dirs() is False
        # exist & merge
        mocked_mkdir.reset_mock()
        maker.merge = True
        maker._create_dirs()
        mocked_mkdir.assert_not_called()
    #: not exist
    with mock.patch('os.path.exists', return_value=False):
        maker.merge = False
        maker._create_dirs()
        mocked_mkdir.assert_any_call(maker.docsDir, 0o755)
        mocked_mkdir.assert_any_call(os.path.join(maker.docsDir, '_build'), 0o755)
        mocked_mkdir.assert_any_call(os.path.join(maker.docsDir, '_static'), 0o755)
        mocked_mkdir.assert_any_call(os.path.join(maker.docsDir, '_templates'), 0o755)


@mock.patch('os.fsync')
def test_create_config_files(mocked_fsync, maker):
    maker.docsDir = gettempdir()

    with mock.patch.object(base, 'open',
                           mock.mock_open(read_data='some data${foo}'),
                           create=True) as mocked_open:
        with mock.patch('os.path.exists', return_value=True) as mocked_exists:
            maker.force = False
            maker._create_config_files()
            assert mocked_exists.call_count == 1
            mocked_open().write.assert_not_called()

            maker.force = True
            mocked_exists.reset_mock()
            maker._create_config_files()
            assert mocked_exists.call_count == 4
            assert mocked_open().write.call_count == 4
            mocked_open.assert_any_call(
                os.path.join(maker.docsDir, 'make.bat'), 'wt')

        with mock.patch('os.path.exists', return_value=False):
            # reset call_count to 0
            mocked_open.reset_mock()
            maker._create_config_files()
            assert mocked_open().write.call_count == 4
            mocked_open.assert_any_call(
                os.path.join(maker.docsDir, 'index.rst'), 'wt')
