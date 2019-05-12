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
def sample_file():
    import shutil

    test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'test_data')
    src_file = os.path.join(test_data_dir, 'sample_setup.cfg')
    dest_file = os.path.join(gettempdir(), 'setup.cfg.txt')
    shutil.copyfile(src_file, dest_file)
    yield dest_file
    # teardown
    os.remove(dest_file)


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


def test_open_with_associated_application(sample_file):
    opener.open_with_associated_application(sample_file, block=True)

    '''
    # non-blocking
    with pytest.raises(Exception) as e:
        utils.open_with_associated_application(testFile)
        os.remove(testFile)
    # linux: CalledProcessError, Windows: WindowsError errno == 2,
    assert e.typename == 'CalledProcessError' or e.typename == 'WindowsError'
    '''
