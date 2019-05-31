#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_readme - pytest module for ReadmeMaker

"""

from __future__ import absolute_import, print_function

import os
import pytest
from tempfile import gettempdir

from skelpy.makers import base, readme, settings
from . import mock


@pytest.fixture()
def maker():
    settings.clear()
    opts = {
        'projectDir': gettempdir(),
        'projectName': 'My Awesome Project',
        'force': False,
    }

    return readme.Maker(**opts)


def test_update_settings(maker):
    assert settings.get('line') == '*' * len('My Awesome Project')


@mock.patch('os.fsync')
def test_write_main(mocked_fsync, maker):
    with mock.patch.object(base, 'open', mock.mock_open(),
                           create=True) as mocked_open:
        with mock.patch('os.path.exists', return_value=True):
            # exist && force == False
            assert not maker.generate()
            mocked_open().write.assert_not_called()
            # exist && force == True
            maker.force = True
            assert maker.generate()
            assert mocked_open().write.called
        with mock.patch('os.path.exists', return_value=False):
            # not exist
            assert maker.generate()
            mocked_open.assert_any_call(
                os.path.join(maker.projectDir, 'README.rst'), 'wt')
