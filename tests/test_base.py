#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_maker - pytest module for MakerMeta and BaseMaker

"""

from __future__ import absolute_import, print_function

import logging
import pytest
import inspect
import string

from skelpy.makers import base
from . import mock


@pytest.fixture(scope='module')
def maker():
    class Demo(base.BaseMaker):
        def generate(self):
            pass

    return Demo()


def test_export(maker):
    #: Maker is a global attribute of this module
    assert inspect.isclass(Maker)
    assert Maker.__name__ == 'Demo'


def test_get_logger(maker):
    assert isinstance(maker.logger, logging.LoggerAdapter)
    assert maker.logger.logger.name == 'skelpy'
    assert maker.logger.extra.get('maker') == Maker.__name__


@mock.patch('os.makedirs')
@mock.patch('os.mkdir')
def test_create_dir(mocked_mkdir, mocked_makedirs, maker):
    #: When the function exits, the patch is undone.
    mocked_error = mock.Mock()
    maker.logger.error = mocked_error

    #: dirs exist
    with mock.patch('os.path.exists', return_value=True):
        # exist & not merge
        maker.merge = False
        assert maker.create_dir('some_dir') == 0
        assert mocked_error.called
        # exist & merge
        mocked_mkdir.reset_mock()
        maker.merge = True
        assert maker.create_dir('some_dir') == -1
        mocked_mkdir.assert_not_called()

    #: not exist
    with mock.patch('os.path.exists', return_value=False):
        maker.merge = False
        assert maker.create_dir('some_dir') == 1
        mocked_mkdir.assert_called_with('some_dir', 0o755)
        mocked_makedirs.assert_not_called()
        # recursive
        mocked_mkdir.reset_mock()
        assert maker.create_dir('some_dir', recursive=True) == 1
        mocked_makedirs.assert_called_with('some_dir', 0o755)
        mocked_mkdir.assert_not_called()


@mock.patch('os.fsync')
@mock.patch.object(base, "get_template", return_value=string.Template('some data${foo}'))
def test_write_file(mocked_template, mocked_fsync, maker):
    #: invalid template file path
    maker.logger.info = mock.Mock()
    maker.logger.error = mock.Mock()

    with mock.patch.object(base, 'open',
                           mock.mock_open(read_data='some data${foo}'),
                           create=True) as mocked_open:
        #: file exist
        with mock.patch('os.path.exists', return_value=True):
            maker.force = False
            maker.write_file('tpl', 'target')
            maker.logger.info.assert_called_with(
                'skipping... '
                + "To overwrite, try -f/--force option")
            mocked_fsync.assert_not_called()

            maker.force = True
            maker.write_file('tpl', 'target')
            maker.logger.info.assert_any_call(
                'overwriting...')
            mocked_open.assert_called_with('target', 'wt')

        #: file NOT exist
        with mock.patch('os.path.exists', return_value=False):
            maker.write_file('tpl', 'target')
            mocked_open.assert_called_with('target', 'wt')

            #: post-job error
            f = mock.Mock(side_effect=Exception("whoops!"))
            mocked_fsync.reset_mock()

            with pytest.raises(Exception):
                ret = maker.write_file('setup', 'target', [f])
                assert ret is None
                f.assert_called()
                maker.logger.error.assert_called()
                mocked_fsync.assert_not_called()

    #: file write error
    with mock.patch.object(base, 'open',
                           mock.mock_open(mock=mock.Mock(side_effect=Exception())),
                           create=True):
        maker.logger.error.reset_mock()
        with pytest.raises(Exception):
            ret = maker.write_file('setup', 'target')
            assert ret is None
            maker.logger.error.assert_called()
