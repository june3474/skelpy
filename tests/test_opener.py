#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_opener - pytest module for functions in utils.opener.py"""

from __future__ import absolute_import, print_function

import sys
import os
import pytest

from tempfile import gettempdir

from skelpy.utils import opener
from . import mock


def test_get_associate_application_cygwin():
    if not sys.platform == 'cygwin':
        return

    app = opener._get_associated_application_cygwin('c:\windows\win.ini')
    assert app == '"C:\\Windows\\system32\\NOTEPAD.EXE"'

    app = opener._get_associated_application_cygwin('.dks')
    assert app is None


def test_get_associated_application_linux():
    if not sys.platform == 'linux':
        return

    app = opener._get_associated_application_linux('/etc/shells')
    editors = ['emacs', 'vi', 'vim', 'gvim', 'pico', 'nano', 'gedit', 'kwrite',
               'kate', 'geany', 'sublime', 'pluma', ]  # anything else?
    assert any(e in app for e in editors)


@mock.patch.object(opener, 'has_command', return_value=False)
def test_open_with_associated_app_linux_without_xdg(mocked_command):
    if not sys.platform.startswith('linux'):
        return

    # test _find_mime() with a sham filename
    with mock.patch('os.path.splitext') as mocked_splitext:
        opener._get_associated_application_linux('kladsjfkls')
        mocked_command.assert_called_with('xdg-mime')
        mocked_splitext.assert_any_call('kladsjfkls')

    # test _find_desktop
    with mock.patch('os.path.exists', return_value=False) as mocked_exists:
        with mock.patch('subprocess.check_output') as mocked_subprocess:
            opener._get_associated_application_linux('sample.txt')
            mocked_subprocess.assert_not_called()
        assert mocked_exists.mock_any_call('/usr/share/applications/mimeinfo.cache')


@mock.patch.object(opener.subprocess, 'call')
def test_open_with_associated_application(mocked_call):
    if sys.platform == 'win32':
        opener.open_with_associated_application('dummy.txt', block=True)
        mocked_call.assert_called_with(['start', '/WAIT', 'dummy.txt'], shell=True)
        # non-blocking
        opener.open_with_associated_application('dummy.txt', 'arg1', 'arg2', block=False)
        mocked_call.assert_called_with(['start', 'arg1', 'arg2', 'dummy.txt'], shell=True)
    elif sys.platform == 'darwin':
        opener.open_with_associated_application('dummy.txt', block=True)
        mocked_call.assert_called_with(['open', '-W', 'dummy.txt'])
        # non-blocking
        opener.open_with_associated_application('dummy.txt', 'arg1', 'arg2', block=False)
        mocked_call.assert_called_with(['open', 'arg1', 'arg2', 'dummy.txt'])
    elif sys.platform == 'cygwin':
        opener.open_with_associated_application('c:\\windows\\win.ini', block=True)
        app = opener._get_associated_application_cygwin('c:\\windows\\win.ini')
        mocked_call.assert_called_with([app, 'c:\\windows\\win.ini'])
        # non-blocking
        opener.open_with_associated_application('c:\\windows\\win.ini', 'arg1', 'arg2', block=False)
        mocked_call.assert_called_with(['cygstart', 'arg1', 'arg2', 'c:\\windows\\win.ini'])
    elif sys.platform.startswith('linux'):
        opener.open_with_associated_application('/etc/shells', block=True)
        app = opener._get_associated_application_linux('/etc/shells')
        mocked_call.assert_called_with([app, '/etc/shells', '&'])
        # non-blocking
        opener.open_with_associated_application('/etc/shells', 'arg1', 'arg2', block=False)
        mocked_call.assert_called_with([app, '/etc/shells', 'arg1', 'arg2'])
