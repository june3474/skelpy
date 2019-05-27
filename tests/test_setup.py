#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_setup - pytest module for SetupMaker

"""

from __future__ import absolute_import, print_function


import os
import pytest
from tempfile import gettempdir

from . import mock
from skelpy.makers import setup as m
from skelpy.makers import settings
from skelpy.utils import helpers


sample_setup_cfg = """[metadata]
name = skelpy
version = 1.0.0
description = A primitive template tool
author = dks, june3474
author_email = dks@faraway.universe
license = ${license}
url = http://faraway.in.universe/
long-description = file: README.rst
platforms = any
classifiers = 
    Development Status :: 5 - Production/Stable
    Topic :: Utilities
    Programming Language :: Python
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    Programming Language :: Python :: 3.6
    Environment :: Console
    Intended Audience :: Developers
    Operating System :: POSIX :: Linux
    Operating System :: Unix
    Operating System :: MacOS
    Operating System :: Microsoft :: Windows

[options]
zip_safe = False
packages = find:
include_package_data = True
package_dir = 
    = src
install_requires = six; awesome
setup_requires =
    setuptools
    another_package
tests_require = pytest

[options.packages.find]
where = src
exclude = 
    tests
    tests.*

[options.extras_require]
all = django; mango

[test]
addopts = tests --verbose
"""

expected_setup = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup


setup(
    name='skelpy',
    version='1.0.0',
    python_requires='>=3',
    url='http://faraway.in.universe/',
    author='dks, june3474',
    author_email='dks@faraway.universe',
    description='A primitive template tool',
    license='${license}',
    package_dir={'': 'src'},
    packages=find_packages(where='src', exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    scripts=[],
    entry_points={
        'console_scripts': [
            'skelpy = skelpy.main:run',
        ],
        # 'gui_scripts': [
        #     'skelpy_gui = skelpy.main_gui:run',
        # ]
    },
    install_requires=[
        'six',
        'awesome'
    ],
    setup_requires=[
        'setuptools',
        'another_package'
    ],
    tests_require=[
        'pytest'
    ],
    extras_require={
        'all': ['django', 'mango']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows'
    ],
)


if __name__ == '__main__':
    setup()
"""


@pytest.fixture(scope='module')
def setup_cfg():
    dest_file = os.path.join(gettempdir(), 'setup.cfg')
    with open(dest_file, 'wt') as f:
        f.write(sample_setup_cfg)
        f.flush()
        os.fsync(f.fileno())
    yield dest_file
    # teardown
    os.remove(dest_file)


@pytest.fixture(scope='module')
def maker(setup_cfg):
    settings.clear()
    settings.update(helpers.read_setup_cfg(setup_cfg))
    settings['projectName'] = settings.get('name')
    return m.SetupMaker(gettempdir(), True)


def test_format(maker):
    # no value
    assert maker._format('') == ''

    # multi_line_list
    text = 'docs\ntests\ntests/*'
    expect = """'docs',
        'tests',
        'tests/*'"""
    assert maker._format(text) == expect
    # ';' separated
    text = 'six; awesome'
    expect = """'six',
        'awesome'"""
    assert maker._format(text) == expect

    # single_line_list
    text = 'docs\ntests\ntests/*'
    ret = maker._format(text, indent=0, sep=', ')
    assert ret == "'docs', 'tests', 'tests/*'"
    # ';' separated
    text = 'six; awesome'
    assert maker._format(text, indent=0, sep=', ') == "'six', 'awesome'"

    # multi_line_dict
    text = "'pdf': ['ReportLab', 'RXP']\n'dks': ['first', 'second']"
    expect = """'pdf': ['ReportLab', 'RXP'],
        'dks': ['first', 'second']"""
    assert maker._format(text, quote=False) == expect


def test_get_python_requires(maker):
    classifiers = """Development Status :: 5 - Production/Stable
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.6
Operating System :: Microsoft :: Windows"""
    python_requires = maker._get_python_requires(classifiers)
    assert python_requires == '>=3'

    classifiers = """Development Status :: 5 - Production/Stable
Programming Language :: Python :: 3.4
Operating System :: Microsoft :: Windows"""
    python_requires = maker._get_python_requires(classifiers)
    assert python_requires == '==3.4'


def test_update_settings(maker, setup_cfg):
    assert settings['author'] == 'dks, june3474'
    assert settings['install_requires'] == ("'six',"
                                                     + '\n        '
                                                     + "'awesome'")
    assert settings['setup_requires'] == ("'setuptools',"
                                                   + "\n        "
                                                   + "'another_package'")
    assert settings['extras_require'] == "'all': ['django', 'mango']"


def test_generate(maker, setup_cfg):
    mocked_info = mock.Mock()
    maker.logger.info = mocked_info

    # setup.py does not exist
    maker.generate()
    setupFile = os.path.join(maker.projectDir, 'setup.py')
    with open(setupFile, 'r') as f:
        content = f.read()
        assert content == expected_setup

    mocked_info.assert_called_with(
        "created file: '{}'".format(setupFile))

    # setup.py existsdata
    with mock.patch.object(m, 'open', mock.mock_open(), create=True) as mocked_open:
        with mock.patch('os.fsync'):
            maker.force = False
            maker.generate()
            mocked_info.assert_any_call(
                "file exists: '{}'".format(setupFile))
            mocked_info.assert_any_call(
                "skipping... "
                + "To overwrite, try -f/--force option")
            mocked_open.assert_not_called()

            maker.force = True
            maker.generate()
            mocked_info.assert_any_call("overwriting...")
            mocked_info.assert_called_with(
                "created file: '{}'".format(setupFile))

    os.remove(setupFile)
