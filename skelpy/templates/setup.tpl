#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup


setup(
    name='${projectName}',
    version='${version}',
    python_requires='${python_requires}',
    url='${url}',
    author='${author}',
    author_email='${author_email}',
    description='${description}',
    license='${license}',
    package_dir={'': '${package_dir}'},
    packages=find_packages(where='${where}', exclude=[${exclude}]),
    zip_safe=${zip_safe},
    include_package_data=${include_package_data},
    scripts=[],
    entry_points={
        'console_scripts': [
            '${projectName} = ${projectName}.main:run',
        ],
        # 'gui_scripts': [
        #     '${projectName}_gui = ${projectName}.main_gui:run',
        # ]
    },
    install_requires=[
        ${install_requires}
    ],
    setup_requires=[
        ${setup_requires}
    ],
    tests_require=[
        ${tests_require}
    ],
    extras_require={
        ${extras_require}
    },
    classifiers=[
        ${classifiers}
    ],
)


if __name__ == '__main__':
    setup()
