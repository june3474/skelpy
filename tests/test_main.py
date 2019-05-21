#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test case for __main__.py

"""

from __future__ import absolute_import, print_function

import os
from skelpy import main
import skelpy.utils.helpers as helpers


def test_parse_projecName():
    cwd = os.getcwd()

    #: empty string(default) in a non-root path
    projectDir, projectName = main._parse_projectName('')
    assert projectDir == os.path.join(cwd)
    assert projectName == os.path.basename(cwd)

    #: empty string in the root path
    root = helpers.root_path()
    os.chdir(root)
    projectDir, projectName = main._parse_projectName('')
    assert projectDir == root
    assert projectName == ''
    os.chdir(cwd)

    #: relative path
    up = os.path.dirname(cwd)
    projectDir, projectName = main._parse_projectName(os.path.join('..', 'dks'))
    assert projectDir == os.path.join(up, 'dks')
    assert projectName == 'dks'

    #: relative path again without any . or ..
    projectDir, projectName = main._parse_projectName('dks')
    assert projectDir == os.path.join(cwd, 'dks')
    assert projectName == 'dks'

    #: one more relative path ending with os.sep
    projectDir, projectName = main._parse_projectName('dks' + os.sep + 'june' + os.sep)
    assert projectDir == os.path.join(cwd, 'dks', 'june')
    assert projectName == 'june'

    #: absolute path
    projectDir, projectName = main._parse_projectName(root + 'dks')
    assert projectDir == os.path.join(root, 'dks')
    assert projectName == 'dks'

    #: absolute path again ending with os.sep
    projectDir, projectName = main._parse_projectName(root + 'dks' + os.sep + 'june' + os.sep)
    assert projectDir == os.path.join(root, 'dks', 'june')
    assert projectName == 'june'

    # improbable but..., just os.sep
    projectDir, projectName = main._parse_projectName(os.sep)
    assert projectDir == root
    assert projectName == ''


def test_main():
    pass
