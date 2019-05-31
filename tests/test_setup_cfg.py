#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_setup_cfg - pytest test module for SetupCfgMaker

"""

from __future__ import absolute_import, print_function

import pytest
import os
from tempfile import gettempdir, tempdir

import skelpy.makers.setup_cfg as m
from skelpy.utils.helpers import read_setup_cfg
from skelpy.makers import settings
from . import mock


@pytest.fixture()
def maker():
    settings.clear()
    # 'description' and 'license' are not given
    opts = {'projectDir': gettempdir(),
            'projectName': 'project',
            'format': 'basic',
            'quiet': True,
            'force': True,
            'test': 'pytest',
            }
    return m.Maker(**opts)


def test_generate(maker):
    mocked_info = mock.Mock()
    maker.logger.info = mocked_info
    cfgFile = os.path.join(maker.projectDir, 'setup.cfg')

    # setup.cfg does not exists
    maker.generate()

    # check if cfgFile has been created
    assert os.path.exists(cfgFile)

    conf_dict = read_setup_cfg(cfgFile)
    assert conf_dict['name'] == '${projectName}'
    assert 'pytest' in conf_dict['tests_require']
    assert conf_dict['package_dir'] == '.'
    assert conf_dict['where'] == '.'

    # now setup.cfg exists
    maker.force = False
    maker.generate()
    mocked_info.assert_any_call(
        "file exists: '{}'".format(cfgFile))
    mocked_info.assert_called_with(
        "skipping... "
        + "To overwrite, try -f/--force option")

    maker.force = True
    maker.format = 'src'
    maker._update_settings()
    maker.generate()
    mocked_info.assert_any_call("overwriting...")
    mocked_info.assert_called_with(
        "created file: '{}'".format(cfgFile))

    conf_dict = read_setup_cfg(cfgFile)
    assert conf_dict['package_dir'] == 'src'
    assert conf_dict['where'] == 'src'

    os.remove(cfgFile)
