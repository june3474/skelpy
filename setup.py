#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from distutils import dir_util
from distutils.filelist import FileList
from setuptools import find_packages, setup
from setuptools.command.sdist import sdist


class ezip(sdist):
    """Create the ezip distribution.

    The ezip distribution is a zip-formatted source distribution which can
    can be run directly as if it were a python module.
    """
    description = "create a zip-formatted executable"

    def run(self):
        self.filelist = FileList()
        self.get_file_list()

        self.make_distribution()

        dist_files = getattr(self.distribution, 'dist_files', [])
        for file in self.archive_files:
            data = ('ezip', '', file)
            if data not in dist_files:
                dist_files.append(data)

    def make_distribution(self):
        with self._remove_os_link():       # Workaround for #516
            base_dir = self.distribution.get_fullname()
            ezip_name = os.path.join(self.dist_dir,
                                     self.distribution.get_name())

            self.make_release_tree(base_dir, self.filelist.files)
            archive_files = []             # remember names of files we create

            file = self.make_archive(ezip_name, 'zip',
                                     root_dir=base_dir,
                                     owner=self.owner, group=self.group)

            archive_files.append(file)
            self.distribution.dist_files.append(('ezip', '', file))
            self.archive_files = archive_files

            if not self.keep_temp:
                dir_util.remove_tree(base_dir, dry_run=self.dry_run)


setup(
    name='skelpy',
    version='1.0.0',
    python_requires='>=2.7',
    url='https://github.com/june3474/skelpy',
    author='dks',
    author_email='june3474@gmail.com',
    description='A simple template tool to create the skeleton for a python project',
    license='MIT',
    package_dir={'': '.'},
    packages=find_packages(where='.', exclude=['docs', 'tests', 'tests.*']),
    # include_package_data with MENIFEST.in does not work. why?
    package_data={
        'skelpy.templates': ['*.tpl', '.gitignore.tpl', '.editorconfig.tpl'],
    },
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
        
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest'
    ],
    extras_require={
        
    },
    classifiers=[
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    cmdclass={'ezip': ezip},
)
