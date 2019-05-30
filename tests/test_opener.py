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


@pytest.fixture(scope='module')
def testFile():
    dest_file = os.path.join(gettempdir(), 'test.txt')
    with open(dest_file, 'wt') as f:
        f.write('dummy text')
        f.flush()
        os.fsync(f.fileno())
    yield dest_file
    # teardown
    os.remove(dest_file)


def test_get_associate_application_cygwin():
    if not sys.platform == 'cygwin':
        return

    app = opener._get_associated_application_cygwin('/cygdrive/c/Windows/win.ini')
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

    # test _find_mime()
    with mock.patch('os.path.splitext') as mocked_splitext:
        opener._get_associated_application_linux('anyfile')
        mocked_command.assert_called_with('xdg-mime')
        mocked_splitext.assert_any_call('anyfile')

    # test _find_desktop
    with mock.patch('os.path.exists', return_value=False) as mocked_exists:
        with mock.patch('subprocess.check_output') as mocked_subprocess:
            opener._get_associated_application_linux('dummy.txt')
            mocked_subprocess.assert_not_called()
        assert mocked_exists.mock_any_call('/usr/share/applications/mimeinfo.cache')


def test_open_with_associated_application(testFile):
    app = None
    if sys.platform == 'cygwin':
        app = opener._get_associated_application_cygwin(testFile)
        opener._get_associated_application_cygwin = mock.Mock(return_value=app)
    elif sys.platform.startswith('linux'):
        app = opener._get_associated_application_linux(testFile)
        opener._get_associated_application_linux = mock.Mock(return_value=app)

    with mock.patch.object(opener.subprocess, 'call') as mocked_call:
        if sys.platform == 'win32':
            opener.open_with_associated_application(testFile, block=True)
            mocked_call.assert_called_with(['start', '/WAIT', testFile], shell=True)
            # non-blocking
            opener.open_with_associated_application(testFile, False, 'arg1', 'arg2')
            mocked_call.assert_called_with(['start', 'arg1', 'arg2', testFile], shell=True)
        elif sys.platform == 'darwin':
            opener.open_with_associated_application(testFile, block=True)
            mocked_call.assert_called_with(['open', '-W', testFile])
            # non-blocking
            opener.open_with_associated_application(testFile, False, 'arg1', 'arg2')
            mocked_call.assert_called_with(['open', 'arg1', 'arg2', testFile])
        elif sys.platform == 'cygwin':
            opener.open_with_associated_application(testFile, block=True)
            mocked_call.assert_called_with([app, testFile])
            # non-blocking
            opener.open_with_associated_application(testFile, False, 'arg1', 'arg2')
            mocked_call.assert_called_with(['cygstart', 'arg1', 'arg2', testFile])
        elif sys.platform.startswith('linux'):
            opener.open_with_associated_application(testFile, block=True)
            mocked_call.assert_called_with([app, testFile])
            # non-blocking
            opener.open_with_associated_application(testFile, False, 'arg1', 'arg2')
            mocked_call.assert_called_with([app, 'arg1', 'arg2', testFile, '&'])
