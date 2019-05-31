#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`DefaultSubCommandArgParser` class"""

from __future__ import absolute_import, print_function

import argparse


class DefaultSubcommandArgParser(argparse.ArgumentParser):
    """Extended :class:`argparse.ArgumentParser` with the feature of setting the default sub-parser

    This class overrides :meth:`ArgumentParse._parse_known_args` to insert
    the default sub-parser to the argument list if no sub-command is given.

    codes by Thomas Grainger, from `stackoverflow
    <https://stackoverflow.com/questions/6365601/default-sub-command-or
    -handling-no-sub-command-with-argparse>`_

    """
    __default_subparser = None

    def set_default_subparser(self, name):
        """set default sub-parser

        Args:
            name (str): sub-parser's name

        Returns:
            None

        """
        self.__default_subparser = name

    def _parse_known_args(self, arg_strings, *args, **kwargs):
        in_args = set(arg_strings)
        d_sp = self.__default_subparser
        if d_sp is not None and not {'-h', '--help'}.intersection(in_args):
            for x in self._subparsers._actions:
                subparser_found = (
                    isinstance(x, argparse._SubParsersAction) and
                    in_args.intersection(x._name_parser_map.keys())
                )
                if subparser_found:
                    break
            else:
                # insert default in first position, this implies no
                # global options without a sub_parsers specified
                arg_strings = [d_sp] + arg_strings
        return super(DefaultSubcommandArgParser, self)._parse_known_args(arg_strings, *args, **kwargs)

    @staticmethod
    def combine_usage(parsers):
        """combine usage-messages of multiple ArgumentParsers into one

        Args:
            parsers (list): ArgumentParsers whose usage-messages to combine

        Returns:
            str: Combined usage-message

        """
        if len(parsers) < 2:
            return ''

        indent = ' ' * len('usage: ')
        combined_usage = []

        # remove the prefix, i.e., "usage: "
        for i, p in enumerate(parsers, 1):
            usage = p.format_usage().split(' ')[1:]
            usage = ' '.join(usage)
            if i > 1:
                usage = indent + usage
            combined_usage.append(usage)

        # add an extra '\n' to the last
        combined_usage[-1] += '\n'

        return ''.join(combined_usage)

    # not used, but leave for future reference
    @staticmethod
    def get_args_by_group(arguments, group):
        """extract arguments that belongs to an argument group

        Args:
            arguments (dict): whole command-line arguments
            group (:class:`argparse._ArgumentGroup`): argument group

        Returns:
            dict: arguments belonged to the group

        """

        # find _group_actions that belongs to the specified group
        group_args = {a.dest: arguments[a.dest] for a in group._group_actions}
        return group_args
