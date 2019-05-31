#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`Logger` class"""

from __future__ import absolute_import, print_function

import logging


class Logger(logging.LoggerAdapter):
    """A simple subclass of :class:`logging.LoggerAdapter` for *skelpy*"""

    def process(self, msg, kwargs):
        """overridden method to insert the `Maker`'s name into the log message.

        This method also add to the *kwargs* the *extra* dict which is passed when constructed.

        Args:
            msg (str): original log message
            kwargs (dict): extra information to pass to the underlying :class:`logging.Logger`

        Returns:
            str: log message modified to include *Maker*'s name
            dict: kwargs plus extra

        """
        kwargs["extra"] = self.extra
        return '[%s] %s' % (self.extra['maker'], msg), kwargs
