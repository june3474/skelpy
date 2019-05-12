#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_logger - SHORT DESCRIPTION HERE

test_logger is a FULL DESCRIPTION HERE
"""

from __future__ import absolute_import, print_function

import pytest
import logging

from skelpy.makers import base
from . import mock


@pytest.fixture(scope='module')
def maker():
    class Demo(base.BaseMaker):
        def generate(self):
            pass

    return Demo()


def test_process(maker):
    maker.logger.logger._log = mock.Mock()
    maker.logger.error("message")
    maker.logger.logger._log.assert_called_with(
        logging.ERROR,
        "[Demo] message",
        mock.ANY,
        extra={'maker': 'Demo'})
