#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module offers :func:`open_with_associated_application` which
opens a file with the associated application.

"""

from __future__ import absolute_import, print_function

import os
import sys

from .helpers import has_command


def _get_associated_application_cygwin(filePath):
    """Helper function to find the appropriate application associated with the given file on cygwin platform

    Args:
        filePath (str):  the file name (possibly including path) to open

        .. Warning::

            filePath should NOT end with '\' or '/'

    Returns:
        str: associated application if any, otherwise None

    """

    import subprocess

    ext = os.path.splitext(filePath)[1]
    if not ext:
        return None

    try:
        ftype = subprocess.check_output(['cmd', '/C', 'assoc', ext])
    except subprocess.CalledProcessError:
        return None
    _, ftype = ftype.split('=', 1)
    ftype = ftype.strip()

    import shlex
    try:
        association = subprocess.check_output(['cmd', '/C', 'ftype', ftype])
    except subprocess.CalledProcessError:
        return None
    _, application = association.split('=', 1)
    application = shlex.split(application, posix=False)[0]
    # still need a final touch for environment variables like %SystemRoot%
    # os.path.expandvars() does not work for % style variables on cygwin
    application = subprocess.check_output(['cmd', '/C', 'echo', application])

    return '"' + application.strip() + '"'  # in case for spaces in 'application'


def _get_associated_application_linux(filePath):
    """Helper function to find the appropriate application associated with the given file on linux platform

    Args:
        filePath (str):  the file name (possibly including path) to open

        .. Warning::

            filePath should NOT end with '\' or '/'

    Returns:
        str: associated application if any, otherwise None

    """

    import subprocess

    try:
        from subprocess import DEVNULL
    except ImportError:
        DEVNULL = open(os.devnull, 'wb')

    # make a ConfigParser instance ready in place
    try:
        from configparser import ConfigParser, NoOptionError  # python 3.x
    except ImportError:
        from ConfigParser import ConfigParser, NoOptionError  # python 2.7

    xdg = has_command('xdg-mime')

    # ------------------------------------------------
    def _find_mime(filePath):
        """Find the proper mime for the given file

        Args:
            filePath (str): file name(possibly including path) to find mime of

        Returns:
            str: mime for the given file if any, otherwise None

        """

        mime = None

        if xdg:
            mime = subprocess.check_output(['xdg-mime', 'query', 'filetype', filePath])
            mime = mime.strip().decode(encoding='utf-8')
        else:  # guess by file extension
            import mimetypes
            ext = os.path.splitext(filePath)[-1]
            mime = mimetypes.types_map.get(ext)

        return mime

    def _find_desktop(mime):
        """Find the proper desktop file for the given mime

        Args:
            mime (str): mime to find corresponding desktop file

        Returns:
            str: desktop file **without** path info

        """

        desktop = None

        if xdg:  # xdg-mime installed
            desktop = subprocess.check_output(['xdg-mime', 'query', 'default', mime])
            if desktop:
                return desktop.strip().decode(encoding='utf-8')

        # if xdg-mime is not available, examine mimeapps.list & mimeinfo.cache in turn
        searchFile = 'mimeapps.list'
        locations = [
            os.path.expanduser('~/.config/'),
            os.path.expanduser('~/.local/share/applications/'),
            ]

        mimeFile = None
        for l in locations:
            if os.path.exists(l + searchFile):
                mimeFile = l + searchFile
                break

        if mimeFile:
            parser = ConfigParser()
            parser.readfile(open(mimeFile))

            try:  # python 2.7 doesn't support 'fallback' option
                desktop = parser.get('Default Applications', mime)
                if desktop:
                    return desktop.split(';')[0]
            except NoOptionError:
                pass

            try:
                desktop = parser.get('Added Associations', mime)
                if desktop:
                    return desktop.split(';')[0]
            except NoOptionError:
                pass

        # if mimeapps.list fails, try mimeinfo.cache
        searchFile = 'mimeinfo.cache'
        locations = [
            '/usr/share/applications/',
            ]

        mimeFile = None
        for l in locations:
            if os.path.exists(l + searchFile):
                mimeFile = l + searchFile
                break

        if mimeFile:
            # reset ConfigParser
            parser = ConfigParser()
            parser.readfp(open(mimeFile))
            try:  # desktop should still be None
                desktop = parser.get('MIME Cache', mime)
                if desktop:
                    return desktop.split(';')[0]
            except NoOptionError:
                pass

        # failed to find appropriate desktop file associated
        return desktop  # still None

    def _find_command(desktop):
        """Find the command out of the given desktop file

        Args:
            desktop (str): desktop file name

        Returns:
            str: command to run

        """

        locations = [
            os.path.expanduser('~/.local/share/applications/'),
            '/usr/share/applications/',
            ]

        dfile = None
        for l in locations:
            dfile = l + desktop
            if os.path.exists(dfile):
                break
        if not dfile:  # no such a desktop file
            return None

        parser = ConfigParser()
        parser.readfp(open(dfile))

        command = None
        try:  # python 2.7 doesn't support fallback option
            command = parser.get('Desktop Entry', 'Exec', raw=True)
        except NoOptionError:
            pass

        if command:
            command = command.split()[0]
            # final check
            if bool(subprocess.call(['which', command], stdout=DEVNULL, stderr=DEVNULL)):
                command = None

        return command
    # ------------------------------------------------------
    #
    # now, find the application
    mime = _find_mime(filePath)
    if not mime:
        return None

    desktop = _find_desktop(mime)
    if not desktop:
        return None

    application = _find_command(desktop)

    return application


def open_with_associated_application(filePath, block=False, *args):
    """Open the file with the associated application using the *"general-purpose opener"* program.

    A *"general-purpose opener"* is a small command-line program which runs the
    specified application associated to the file type. In a rough sense,
    what *general-purpose opener* does is like double-clicking the file.
    Below are well known OSes and their *general-purpose openers*::

        - Linux: ``xdg-open``
        - Windows: ``start``
        - OS X: ``open``
        - Cygwin: ``cygstart``

    .. Note::

        Although :func:`subprocess.call` is a blocking function, Most--well,
        if not all--general-purpose openers, by default, do not wait until
        the application terminates. For kind-of blocking mode, Windows(``start``)
        and OSX(``open``) provide waiting option "/WAIT" and "-W", respectively.
        So, it is possible to run the associated application in the blocking mode
        just by invoking the *general-purpose opener* with a file name with those
        options. For example, on Windows::

           start -W sample.txt

       would make a text editor such as ``notepad.exe` open the sample.txt file
       and wait until notepad terminates.

       However, it is **not** possible on linux and cygwin, because their
       *general-purpose openers* do not have such options.
       Thus, for the same effect on linux and cygwin, we have to directly run
       the associated application with the file

       Also be informed that :func:`startfile` function provided by python
       :mod:`os` module is only for Windows and non-blocking.

    Args:
        filePath (str): the file name(possibly including path) to open
        block (bool): if True, execute the application in the blocking mode,
            i.e., wait until the application terminates, otherwise non-blocking
        args (str): other arguments to pass to the application to be invoked

    Returns:
        int: retcode of :func:`subprocess.call` if the application successfully runs,
        otherwise, i.e., when failed to find an associated application, returns -1

    """

    import subprocess

    cmd = []

    platform = sys.platform
    if platform == 'win32':
        cmd.append('start')
        # cmd.append('""')  # window title
        if block:
            cmd.append('/WAIT')
        cmd.extend(args)
        cmd.append(filePath)
        # On Windows, "start" is a part of "cmd." so subprocess.call without
        # "shell=True" would't work
        return subprocess.call(cmd, shell=True)
    elif platform == 'darwin':
        cmd.append('open')
        if block:
            cmd.append('-W')
        cmd.extend(args)
        cmd.append(filePath)
        return subprocess.call(cmd)
    elif platform == 'cygwin':
        if block:
            cmd.append(_get_associated_application_cygwin(filePath))
        else:
            cmd.append('cygstart')
        cmd.extend(args)
        cmd.append(filePath)
        try:
            return subprocess.call(cmd)
        except TypeError:  # in case that application is None
            return -1
    elif platform.startswith('linux'):
        cmd.append(_get_associated_application_linux(filePath))
        cmd.extend(args)
        cmd.append(filePath)
        if not block:
            cmd.append('&')  # instead of checking xdg-mime installed, simply running background
        try:
            return subprocess.call(cmd)
        except TypeError:  # in case that application is None
            return -1

    return -1

