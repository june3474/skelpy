#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""${description}

"""

from __future__ import absolute_import, print_function

import sys
from argparse import ArgumentParser


def main(argv=None):
    """driver module to run ${projectName}."""

    if argv is None:
        argv = sys.argv[1:]

    try:
        # parse command-line options
        parser = ArgumentParser(description='${description}')
        parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                            help='print verbose messages [default: %(default)s]')

        # ADD MORE ARGUMENTS IF NEEDED #

        opts = vars(parser.parse_args(argv))

    except Exception as e:
        indent = ' ' * len('${projectName}: ')
        sys.stderr.write('${projectName}: ' + repr(e) + '\n')
        sys.stderr.write(indent + "for help, use --help")
        return 2

        # MAIN BODY #


def run():
    """Entry point for console script"""
    main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(run())
