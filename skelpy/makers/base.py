#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module defines :class:`MakerMeta` and :class:`BaseMaker` classes"""

from __future__ import print_function, absolute_import

import sys
import os
import logging
from abc import ABCMeta, abstractmethod

from skelpy.utils.helpers import add_metaclass
from skelpy.utils.logger import Logger
from skelpy.templates import get_template
from . import settings


class MakerMeta(ABCMeta):
    """Metaclass for :class:`BaseMaker` class

    ``MakerMeta`` is a metaclass which subclasses :class:`ABCMeta`.
    In addition to the features of its superclass :class:`!ABCMeta`,
    This metaclass provides all subclasses of :class:`BaseMaker` class
    with extra works of calling :func:`_export` and :func:`_get_logger`
    functions when they are first imported.

    Args:
        className (str): class name
        superClasses (:obj:`class`): parent classes
        attrDict (dict): dictionary of attributes

    """
    def __init__(cls, className, superClasses, attrDict):
        super(MakerMeta, cls).__init__(className, superClasses, attrDict)
        cls._export()
        cls._get_logger()


@add_metaclass(MakerMeta)
class BaseMaker(object):
    """Abstract class for *Maker* classes"""

    def __init__(self):
        pass

    @classmethod
    def _export(cls):
        """set the module-level variable(attribute) ``Maker``

        ``Maker`` is set to the *Maker* class defined in the module.

        For example, if you define a *Maker* class ``AwesomeMaker`` in the
        module named``awesome``, ``Maker`` attribute of ``awesome`` module,
        i.e., ``awesome.Maker`` would be set to the class ``AwesomeMaker``.
        This functionality makes it easy to identify a *Maker* class defined
        in a module just by importing the module.

        This class method is automatically run by the :class:`MakerMeta`
        metaclass when a module containing a subclass of :class:`BaseMaker`
        is first imported.

        Args:
            cls (:obj:`class`): the most specific--i.e., lowest--*Maker* class.

        Returns:
            none

        """
        sys.modules[cls.__module__].Maker = cls

    @classmethod
    def _get_logger(cls):
        """setup a logger--actually :class:`LoggerAdapter`--for the class
        
        Like :method:`_export`, this class method is automatically run by the
        :class:`MakerMeta` metaclass too.

        Args:
            cls (class): the most specific--i.e., lowest--Maker class.

        Returns:
            None

        """

        cls.logger = Logger(logging.getLogger('skelpy'), {'maker': cls.__name__})

    def create_dir(self, target_dir, recursive=False):
        """create a directory

        The default mode is 0777 (octal). If the directory to create exists,
        this method does nothing.

        Args:
            target_dir (str): directory path to create
            recursive (bool): create a directory recursively, i.e., makes all
                intermediate-level directories needed to contain the target_dir.

        Returns:
            int: ``1`` if the directory is newly created; ``-1`` if the directory
            exists and ``--merge`` option is ``True``; ``0`` if if the directory
            exists and ``--merge`` option is ``False``.

        Raises:
            OSError(python 2.7) or PermissionError(python 3.x)

        """
        cmd = os.makedirs if recursive else os.mkdir
            
        if os.path.exists(target_dir):
            self.logger.info("directory exists: '{}'".format(target_dir))

            if self.merge:
                self.logger.info(
                    "Project will merge with the existing directory.")
                return -1
            else:
                self.logger.error(
                    "To overlap onto the existing directory, "
                    "try -m/--merge option.")
                return 0

        cmd(target_dir, 0o755)
        self.logger.info("created directory: '{}'".format(target_dir))

        return 1

    def write_file(self, template, target_file, post_jobs=[]):
        """create a file based on the given *template*.

        *template* could be a string(template-file-name) or
        an instance of :class:`string.Template`.
        If the file to create exists already, the behavior of this method
        depends on the ``--force`` option. If ``force`` option is True,
        the new file will overwrite the existing file. Otherwise,
        it does noting.

        Before writing the file, this method performs
        :meth:`string.Template.safe_substitute` with values in :attr:`makers.settings`.

        .. note::

            Functions in ``post_jobs`` list are run after ``safe_substitute()``
            and before writing the final target_file.

        Args:
            template (:obj:`string.Template` or str): :obj:`string.Template` object
                or the name of a template file.
            target_file (str): file path to create
            post_jobs (:obj:`list` of :obj:`str`): list of functions or callable
                object that would run after doing :meth:`Template.safe_substitute`.

                .. warning::

                    Each function in the ``post_jobs`` should take a ``str`` as its
                    argument, which is, in effect, the return value of the
                    :meth:`string.Template.safe_substitute`.

        Returns:
            str or None: *target_file*, i.e., path of the newly created file
                if successful, None otherwise.

        """
        if type(template) is str:
            tpl = get_template(template)
            if not tpl:
                self.logger.warning(
                    "failed to retrieve the template file: '{}.tpl'".format(template))
                return
            else:
                template = tpl

        if os.path.exists(target_file):
            self.logger.info("file exists: '{}'".format(target_file))

            if self.force:
                self.logger.info(
                    "overwriting...")
            else:
                self.logger.info(
                    "skipping... "
                    "To overwrite, try -f/--force option")
                return

        content = template.safe_substitute(**settings)
        try:
            if post_jobs:
                for f in post_jobs:
                    content = f(content)
        except Exception as e:
            self.logger.error(
                "Error: failed to apply the post-job function '{}'\n".format(f.__name__) + repr(e))
            return

        try:
            with open(target_file, 'wt') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            self.logger.error(
                "Error: failed to write '{}'\n".format(target_file) + repr(e))
            return

        self.logger.info("created file: '{}'".format(target_file))

        return target_file

    @abstractmethod
    def generate(self):
        """ Abstract method that all subclasses must implement.

        All *Maker* classes should do their jobs by overriding this method.

        Returns:
            bool: True if successful, False otherwise

        """
        raise NotImplementedError
