#!/usr/bin/env python
# encoding: utf-8
"""Other helper functions"""

from __future__ import print_function, absolute_import

import sys
import os


def is_valid_identifier(string):
    """Check if the string is a valid project/package name.

    .. note::

        Valid characters for ``projectName`` are::

            * uppercase and lowercase letters A through Z
            * underscore '_'
            * the digits 0 through 9 except for the first character

    Args:
        string (str): project/package name

    Returns:
        bool: True if string is valid project/package name else False

    """

    import re
    import keyword

    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", string):
        return False
    if keyword.iskeyword(string):
        return False

    return True


def has_command(cmd):
    """Check if the given command is available on the system

    Args:
        cmd (str): command to check
    Returns:
        bool: True if available, otherwise False
    """

    import subprocess

    try:
        from subprocess import DEVNULL
    except ImportError:
        DEVNULL = open(os.devnull, 'wb')

    if sys.platform == 'win32':
        checker = 'where'
    else:  # linux, OSX, cygwin
        checker = 'which'

    return not bool(subprocess.call([checker, cmd], stdout=DEVNULL, stderr=DEVNULL))


def has_module(modName):
    """Check if the module is installed

    Args:
        modName (str): module name to check

    Returns:
        bool: True if installed, otherwise False

    """

    from pkgutil import iter_modules

    return modName in (name for loader, name, ispkg in iter_modules())


def get_gitConfig():
    """read ``.gitconfig`` file in the user's ``$HOME`` directory, if exists

    Returns:
        :class:`ConfigParser` or None: ConfigParser object filled with info
        read from ``.gitconfig``

    """
    import errno
    try:
        from configparser import ConfigParser
    except ImportError:
        from ConfigParser import ConfigParser

    home = 'HOMEPATH' if sys.platform == 'win32' else 'HOME'
    git_config_file = os.path.join(os.environ[home], '.gitconfig')
    try:
        with open(git_config_file, 'r') as f:
            data = f.readlines()
    except (IOError, OSError) as e:   # no .gitconfig
        if e.errno == errno.ENOENT:
            return None

    try:
        from StringIO import StringIO  # python 2
    except ImportError:
        from io import StringIO  # python 3

    # white space on the left side hinders ConfigParse's parsing
    stripped_data = ''.join([line.lstrip() for line in data])
    fp = StringIO(stripped_data)
    gitConfig = ConfigParser()
    if sys.version_info[0] == 2:
        gitConfig.readfp(fp)
    else:
        gitConfig.read_file(fp)

    return gitConfig


def get_userName():
    """read the user's name from ``.gitconfig`` file in the ``$HOME`` directory or
    the environmental variable ``USER``

    Returns:
        str: user's name

    """
    try:
        from configparser import NoOptionError
    except ImportError:
        from ConfigParser import NoOptionError

    name = ''

    # first, try .gitconfig
    gitConfig = get_gitConfig()
    if gitConfig:
        try:
            name = gitConfig.get('user', 'name')
        except (KeyError, NoOptionError):
            pass

    # if fail, try environment variables
    if not name:
        user = 'USERNAME' if sys.platform == 'win32' else 'USER'
        name = os.environ.get(user, '')

    return name


def get_email():
    """read the user's name from ``.gitconfig`` file in the ``$HOME`` directory.

    If ``.gitconfig`` file does not exist, this function improvises an email
    address by concatenating user's name and host name.

    Returns:
        str: user's email address

    """
    from six.moves.configparser import NoOptionError

    email = ''

    gitConfig = get_gitConfig()
    if gitConfig:
        try:
            email = gitConfig.get('user', 'email')
        except (KeyError, NoOptionError):
            pass

    # if not successful, we improvise
    if not email:
        import socket
        user = get_userName()
        host = socket.gethostname()
        email = "{user}@{host}".format(user=user, host=host)

    return email


def get_python_version(short=False):
    """get system's python version

    Args:
        short (bool): select the short version number(major.minor only) or not

    Returns:
        str: major.minor if *short* is True, major.minor.release otherwise

    """
    long_ver = sys.version.split()[0]
    short_ver = '.'.join(long_ver.split('.')[:2])
    return short_ver if short else long_ver


def remove_comment_lines_in_str(text_data):
    """remove comment lines in binary data

    Lines starting with '#' or '!' or 'REM' are considered to be comments.

    borrowed from `stackoverflow <https://stackoverflow.com/questions/28401547/how-to-remove-comments-from-a-string>`__

    .. comment: two underscores are needed above link

    Args:
        text_data (str): string to process

    Returns:
        str: string with removed comments

    """
    try:
        from StringIO import StringIO  # python 2
    except ImportError:
        from io import StringIO  # python 3

    newData = ''

    for line in StringIO(text_data).readlines():
        # rstrip() will keep the _indent but remove all white spaces including '\n'
        stripped_line = line.strip()
        line = line.rstrip()
        # The Shebang line should survive. shouldn't she?
        if stripped_line.startswith(('#!', '# -*-')):
            newData += line + '\n'
        # user wants to leave a comment
        elif stripped_line.startswith(('##', '!!')):
            newData += line.replace(stripped_line[0:2], stripped_line[:1], 1) + '\n'
        # Also keep existing empty lines
        elif not stripped_line:
            newData += line + '\n'
        # But remove lines that only contains comments
        elif stripped_line.startswith(('#', '!', 'REM')):
            pass
        else:
            # the comments after the code will remain.
            newData += line + '\n'

    return newData


def remove_comment_lines_in_file(oldFile, newFile=None):
    """remove comment lines in a file

    Lines starting with '#' or '!' or 'REM' are considered to be comments.

    Args:
        oldFile (str): file name(possibly including path) to remove comments
        newFile (str): file name with being removed comments. if this argument is
            not provided or None(default), the newly created file will overwrite the old.

    Returns:
        None

    """
    with open(oldFile, 'r') as f:
        data = f.read()

    comment_free_data = remove_comment_lines_in_str(data)
    if not newFile:
        newFile = oldFile

    with open(newFile, 'wt') as f:
        f.write(comment_free_data)
        f.flush()
        os.fsync(f.fileno())


def read_setup_cfg(cfg_file):
    """read ``setup.cfg`` file

    ``cfg_file`` may contain a path

    Note:

        :func:`setuptools.config.read_configuration` has a `problem with encoding under python2`_

    Args:
        cfg_file (str): path of ``setup.cfg`` file

    Returns:
        dict: information read from the setup.cfg file  if successful, otherwise an empty dict.

    .. _problem with encoding under python2:
        https://github.com/pypa/setuptools/issues/1136

    """
    conf_dict = {}

    try:
        from StringIO import StringIO  # python 2
    except ImportError:
        from io import StringIO  # python 3

    try:
        from configparser import ConfigParser  # python3
    except ImportError:
        from ConfigParser import ConfigParser  # python2

    try:
        with open(cfg_file, 'r') as f:
            data = f.read()
            content = StringIO(remove_comment_lines_in_str(data))
    except IOError:
        return conf_dict

    parser = ConfigParser()
    if sys.version_info[0] == 2:
        parser.readfp(content)
    else:
        parser.read_file(content)

    # prevent pollution by too many options
    sections_to_read = ['metadata', 'options', 'options.packages.find']
    for section in sections_to_read:
        options = parser.options(section)
        for opt in options:
            value = parser.get(section, opt)
            conf_dict[opt] = value[1:] if value.startswith('\n') else value

    # remove leading '=' of package_dir
    package_dir = conf_dict['package_dir']
    conf_dict['package_dir'] = package_dir.split('=')[-1].strip()

    # special handling for 'extras_require' section
    section = 'options.extras_require'
    require = []
    options = parser.options('options.extras_require')
    for opt in options:
        val_list = parser.get(section, opt).split('; ')
        require.append(repr(opt) + ': ' + str(val_list))
    conf_dict['extras_require'] = '\n'.join(require)

    return conf_dict


def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass.

    This function was copied from `six library <https://pypi.org/project/six>`_
    """
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


def is_rootDir(path):
    """check if the path given is the root directory

    Args:
        path (str): path to check

    Returns:
        bool: True if the *path* is root directory, False otherwise
    """
    if path == '':
        return False

    return os.path.dirname(path) == path


def root_path():
    """get the root path

    This function is OS-independent.
    """
    return os.path.abspath(os.sep)
