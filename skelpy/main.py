#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""entry point to skelpy

main.py is the front-end module that parses the command line options and creates
the project-structure accordingly.
"""

from __future__ import absolute_import, print_function

import sys
import logging
import os

from skelpy.makers import settings, get_maker
from skelpy.utils.defaultsubparse import DefaultSubcommandArgParser
import skelpy.utils.helpers as helpers


def _setup_arg_parser():
    """Setup command-line option parser

    """
    parser = DefaultSubcommandArgParser()
    subparsers = parser.add_subparsers(title='sub-command')

    #: main options
    #: setting 'prog' prevents showing subparser's name in the usage output
    main_parser = subparsers.add_parser('template',
                                        prog='skelpy',
                                        description='A simple template tool for a python project.',
                                        epilog="For the 'license' sub-command, see 'skelpy license --help'.")

    main_parser.add_argument('projectName', metavar='ProjectName', nargs='?',
                             default='', help='project(directory) name to create')
    main_parser.add_argument('-F', '--format', default='basic',
                             choices=['basic', 'src'],
                             help='format of directory structure [default: %(default)s]')
    main_parser.add_argument('-T', '--test', default='pytest',
                             choices=['unittest', 'pytest'],
                             help='testing tool [default: %(default)s]')
    main_parser.add_argument('-q', '--quiet', action='store_true',
                             help='skip editing setup.cfg file [default: %(default)s]')
    main_parser.add_argument('-m', '--merge', action='store_true',
                             help='overlap project onto existing directory [default: %(default)s]')
    main_parser.add_argument('-f', '--force', action='store_true',
                             help='overwrite existing files [default: %(default)s]')
    main_parser.add_argument('-v', '--verbose', action='store_true',
                             help='show verbose messages [default: %(default)s]')

    #: license sub-command options
    lic_parser = subparsers.add_parser('license', prog='skelpy license')
    lic_parser.add_argument('license', metavar='LICENSE', nargs='?', default=None,
                            help='new license to create or change to')
    lic_parser.add_argument('-l', '--list', action='store_true',
                            help='show licenses supported by templater')
    lic_parser.add_argument('-v', '--verbose', action='store_false',
                            help='show verbose messages [default: %(default)s]')

    #: assign a front-end function to each sub-parser
    main_parser.set_defaults(func=_skel)
    lic_parser.set_defaults(func=_license)
    #: set the default sub-parser to main_parser
    parser.set_default_subparser('template')
    #: combine usage messages of main_parser and lic_parser
    main_parser.usage = parser.combine_usage([main_parser, lic_parser])
    #: replace the top-most parser's usage and help messages for main sub-parser's
    parser.format_usage = main_parser.format_usage
    parser.format_help = main_parser.format_help
    #: for easy reference to sub-parsers
    parser.main_parser = main_parser
    parser.lic_parser = lic_parser

    return parser


def _setup_logger():
    """setup the root logger

    Returns:
        none

    """
    FORMAT = '%(asctime)-s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)


def _parse_projectName(projectName):
    """parse :attr:`projectName` to get sheer projectName and projectDir

    After parsing, this method updates ``projectDir`` and ``projectName`` values
    in :attr:`settings`

    Args:
        projectName (str): project name the user input, possibly contains path

    Returns:
        tuple: (projectDir, projectName)

        .. note::
           projectDir should include the *projectName* as its the last components,
           In other words, the following statement must be True.

               ``os.path.split(projectDir)[-1] == projectName``

    """
    root = helpers.root_path()

    if not projectName:
        projectDir = os.getcwd()
        #: run in the root directory but did not provide project name
        if helpers.is_rootDir(projectDir):
            return projectDir, ''
        #: not in the root directory
        projectName = os.path.split(projectDir)[-1]
    elif os.path.abspath(projectName) == root:   # maybe too much?
        return root, ''
    else:
        #: remove trailing os.sep
        if projectName.endswith(os.sep):
            projectName, _ = os.path.split(projectName)

        #: if the path given is not absolute, abspath() returns getcwd() + path
        #: abspath() includes normpath()
        projectDir = os.path.abspath(projectName)
        projectName = os.path.split(projectDir)[-1]

    return projectDir, projectName


def _skel(opts, parser):
    """create the skeleton of a python project

    Args:
        opts (dict): arguments passed from command line, i.e, sys.argv[1:]
        |FYI, sub-command is not passed
        parser (obj): instance of :class:`DefaultSubcommandArgParser` class

    Returns:
        bool

    """
    projectDir, projectName = _parse_projectName(opts['projectName'])
    if not projectName:
        sys.stderr.write(
            "[skelpy] Invalid project name: {}\n".format(projectName))
        return False

    opts['projectDir'] = projectDir
    opts['projectName'] = projectName
    settings.update(opts)

    maker_cls = get_maker('project')
    if not maker_cls:
        return False

    maker = maker_cls(**settings)
    if not maker.generate():
        return False

    return True


def _license(opts, parser):
    """do license sub-command jobs, i.e., creating or changing a license

    Args:
        opts (dict): arguments passed from command line, i.e, sys.argv[1:]
        |FYI, sub-command is not passed
        parser (obj): instance of :class:`DefaultSubcommandArgParser` class

    Returns:
        None

    """
    #: if neither list option nor license argument is given
    if not opts.get('list') and not opts.get('license'):
        # ArgumentParser.error() terminates the process.
        # no need to call return of sys.exit()
        parser.lic_parser.error(
            "Either '-l/--list' option or 'LICENSE' argument is required.")
        return False

    maker_cls = get_maker('license_change')
    if not maker_cls:
        sys.stderr.write(
            "[skelpy] Maker module not found: 'license_change.py'\n")
        return False

    maker = maker_cls(**opts)
    return maker.generate()


def run(argv=None):
    """driver to run ``skelpy``

    """
    _setup_logger()

    if argv is None:
        argv = sys.argv[1:]
    try:
        parser = _setup_arg_parser()
        opts = vars(parser.parse_args(argv))

    except Exception as e:
        sys.stderr.write("[skelpy] " + repr(e) + "\n")
        sys.stderr.write("For help, use --help\n")
        return 2

    # MAIN BODY #
    if not opts.pop('verbose'):
        logging.disable(logging.CRITICAL)

    func = opts.pop('func')
    if func(opts, parser):
        sys.stdout.write('Successfully done.\n')
        return 0
    else:
        sys.stdout.write('Failed.\n')
        parser.print_usage()
        return 1


if __name__ == "__main__":
    sys.exit(run())
