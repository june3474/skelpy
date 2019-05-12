[metadata]
name = ${projectName}
version = ${version}
author = ${author}
author_email = ${author_email}
description = ${description}
long-description = file: README.rst
url = https://github.com/${author}/${projectName}
license = ${license}
platforms = any
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers =
    Environment :: Console
	# Environment :: Win32 (MS Windows)
	# Environment :: X11 Applications :: Qt
    Operating System :: OS Independent
    # Programming Language :: Python :: 2.7
    # Programming Language :: Python :: 3
    # Programming Language :: Python :: 3.5
    Programming Language :: Python :: ${python_version_short}
    Topic :: Utilities

[options]
zip_safe = False
packages = find:
include_package_data = True
package_dir =
	= ${package_dir}
install_requires =
setup_requires = ${pytest_runner}
tests_require = ${pytest}

[options.extras_require]

[options.packages.find]
where = ${package_dir}
exclude =
    docs
    tests
    tests.*

[aliases]
docs = build_sphinx
release = sdist bdist_wheel upload
${pytest_alias}
[tool:pytest]
addopts =
    --verbose
norecursedirs =
    dist
    build
    .tox

[bdist_wheel]
universal = 0

[build_sphinx]
source_dir = docs
build_dir = docs/_build
