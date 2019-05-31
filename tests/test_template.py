#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pytest module for :func:`template.get_template` package function"""

from __future__ import absolute_import, print_function

import string
from skelpy.templates import get_template


def test_get_template():
    #: empty argument
    ret = get_template('invalid')
    assert ret is None

    #: invalid template
    ret = get_template('invalid')
    assert ret is None

    #: normal case
    ret = get_template("setup")
    assert isinstance(ret, string.Template)
    assert "from setuptools import find_packages, setup" in ret.template
