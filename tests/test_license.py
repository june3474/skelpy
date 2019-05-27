#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_license - pytest module for LicenseMaker

"""

import os
import pytest

from tempfile import gettempdir

from skelpy.makers import base, license, settings
from . import mock


@pytest.fixture(scope='module')
def maker():
    settings.clear()
    opts = {'projectDir': gettempdir(),
            'force': False,
            'license': 'GPL2',
            }

    return license.Maker(**opts)


def test_is_supported_license(maker):
    assert maker.is_supported_license('Foo') is False
    assert maker.is_supported_license('${description}') is False
    assert maker.is_supported_license('mozilla') is True


@mock.patch.object(base, 'get_template')
@mock.patch('os.fsync')
def test_generate(mocked_fsync, mocked_get_template, maker):
    mocked_info = mock.Mock()
    maker.logger.info = mocked_info

    maker.license = 'CC0'
    licFile = os.path.join(maker.projectDir, 'LICENSE')

    with mock.patch.object(base, 'open', mock.mock_open(),
                           create=True) as mocked_open:
        with mock.patch('os.path.exists', side_effect=[True, True, False]):
            # LICENSE file exists && force is False
            maker.force = False
            maker.generate()
            mocked_info.assert_any_call(
                "file exists: '{}'".format(licFile))
            mocked_open().write.assert_not_called()

            # LICENSE file exists && force is True
            maker.force = True
            maker.generate()
            mocked_info.assert_any_call(
                "overwriting...")
            mocked_get_template.assert_called_with("license_cc0_1.0")
            assert mocked_open().write.called

            # LICENSE does not exist
            mocked_open.reset_mock()
            maker.license = 'MOZILLA'
            maker.generate()
            mocked_get_template.assert_called_with("license_mozilla")
            assert mocked_open().write.called
            mocked_info.assert_called_with(
                "created file: '{}'".format(licFile))
