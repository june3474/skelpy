#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_utils - pytest module for tools in helpers.py

"""

from __future__ import absolute_import, print_function

import os
import sys
from tempfile import gettempdir

import pytest

import skelpy.utils.helpers as helpers
from . import mock


test_data = ("#!/usr/bin/env python - shebang will remain.\n"
             "# -*- coding: utf-8 -*-\n"
             "# This line will go.\n"
             "\t! And this line too. but not the empty line below.\n"
             "\n"
             "## this line will survive. make sure that there's a empty line above.\n"
             "!! this line will too.\n"
             "[metadata]  # keep this normal line and this comment, too.\n"
             "name = ${project} # comments after special tokens are OK as well.\n"
             "\n"
             "classifiers=\n"
             "    Environment :: Console  # _indent will be kept\n"
             "    ## Environment :: Win32 (MS Windows) # what about this?\n")

expected = ("#!/usr/bin/env python - shebang will remain.\n"
            "# -*- coding: utf-8 -*-\n"
            "\n"
            "# this line will survive. make sure that there's a empty line above.\n"
            "! this line will too.\n"
            "[metadata]  # keep this normal line and this comment, too.\n"
            "name = ${project} # comments after special tokens are OK as well.\n"
            "\n"
            "classifiers=\n"
            "    Environment :: Console  # _indent will be kept\n"
            "    # Environment :: Win32 (MS Windows) # what about this?\n")


@pytest.fixture(scope='module')
def test_file():
    testFile = os.path.join(gettempdir(), 'test_file')
    with open(testFile, 'wt') as f:
        f.write(test_data)

    yield testFile
    os.remove(testFile)


def test_get_gitConfig_with_gitconfig():
    git_data = '[user]\n\tname = june3474\n\temail = june3474@email\n[core]\n\tautocrlf = true\n'

    with mock.patch.object(helpers, 'open', mock.mock_open(read_data=git_data), create=True):
        gitConfig = helpers.get_gitConfig()
        assert gitConfig.__class__.__name__ == 'ConfigParser'
        assert gitConfig.get('user', 'name') == 'june3474'
        assert gitConfig.get('user', 'email') == 'june3474@email'


@mock.patch('os.path.join', return_value='NOTEXIST')
def test_get_gitConfig_without_gitconfig(mocked_join):
    gitConfig = helpers.get_gitConfig()
    assert gitConfig is None


def test_get_userName():
    assert helpers.get_userName() not in ('', None)


def test_get_email():
    assert helpers.get_email() not in ('', None)


def test_remove_comment_line_in_str():
    assert helpers.remove_comment_lines_in_str(test_data) == expected


def test_remove_comment_line_in_file(test_file):
    destFile = os.path.join(gettempdir(), 'destFile')

    helpers.remove_comment_lines_in_file(test_file, destFile)
    with open(test_file, 'r') as f:
        data = f.read()
    assert data == test_data

    with open(destFile, 'r') as f:
        data = f.read()
    assert data == expected

    # overwrite
    helpers.remove_comment_lines_in_file(test_file)
    with open(test_file, 'r') as f:
        data = f.read()
    assert data == expected

    os.remove(destFile)


def test_read_setup_cfg():
    import shutil

    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    src_file = os.path.join(test_data_dir, 'sample_setup.cfg')
    dest_file = os.path.join(gettempdir(), 'setup.cfg')
    shutil.copyfile(src_file, dest_file)

    conf_dict = helpers.read_setup_cfg(dest_file)
    os.remove(dest_file)

    assert conf_dict.get('name') == 'skelpy'
    assert conf_dict.get('license') == '${license}'

    # after removing dest_file
    assert helpers.read_setup_cfg(dest_file) is None


def test_is_rootDir():
    cwd = os.getcwd()

    assert helpers.is_rootDir('') is False
    assert helpers.is_rootDir('dks') is False

    if sys.platform == 'win32':
        assert helpers.is_rootDir('c:\\') is True
        assert helpers.is_rootDir('c:\\dks') is False
        os.chdir('C:\\Windows')
        assert helpers.is_rootDir(os.getcwd()) is False
        os.chdir('C:\\')
        assert helpers.is_rootDir(os.getcwd()) is True
        os.chdir(cwd)
    else:
        assert helpers.is_rootDir('/') is True
        assert helpers.is_rootDir('//') is True
        assert helpers.is_rootDir('dks') is False
        os.chdir('/tmp')
        assert helpers.is_rootDir(os.getcwd()) is False
        os.chdir('/')
        assert helpers.is_rootDir(os.getcwd()) is True
        os.chdir(cwd)
