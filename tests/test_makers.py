#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_makers - pytest module for makers package

"""

from __future__ import absolute_import, print_function

from tempfile import gettempdir
from skelpy.makers import get_maker, settings
from skelpy.makers.docs import DocMaker

settings['projectName'] = 'project'


def test_get_maker():
    M = get_maker('docs')
    assert M is not None
    assert isinstance(M(gettempdir(), True, True), DocMaker)

    M = get_maker('invalid')
    assert M is None
