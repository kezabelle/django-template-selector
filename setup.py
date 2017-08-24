#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from setuptools import setup, __version__ as setuptools_version
from setuptools.command.test import test as TestCommand

INSTALL_REQUIRES = []
EXTRA_REQUIRES = {}
scandir = "scandir>=1.5"
if int(setuptools_version.split(".", 1)[0]) < 18:
    assert "bdist_wheel" not in sys.argv, "setuptools 18 required for wheels."
    # For legacy setuptools + sdist.
    if sys.version_info[0] == 2:
        INSTALL_REQUIRES.append(scandir)
else:
    EXTRA_REQUIRES[":python_version<'3'"] = [scandir]

if sys.version_info[0] == 2:
    # get the Py3K compatible `encoding=` for opening files.
    from io import open
HERE = os.path.abspath(os.path.dirname(__file__))


class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def make_readme(root_path):
    consider_files = ("README.rst", "LICENSE", "CHANGELOG", "CONTRIBUTORS")
    for filename in consider_files:
        filepath = os.path.realpath(os.path.join(root_path, filename))
        if os.path.isfile(filepath):
            with open(filepath, mode="r", encoding="utf-8") as f:
                yield f.read()

LICENSE = "BSD License"
URL = "https://github.com/kezabelle/django-template-selector"
LONG_DESCRIPTION = "\r\n\r\n----\r\n\r\n".join(make_readme(HERE))
SHORT_DESCRIPTION = "Provides a model field and form field for allowing users to select a template file"
KEYWORDS = (
    "django",
    "templateselector",
    "widget",
    "model",
    "form",
    "field",
)

setup(
    name="django-templateselector",
    version="0.2.3",
    author="Keryn Knight",
    author_email="django-templateselector@kerynknight.com",
    maintainer="Keryn Knight",
    maintainer_email="django-templateselector@kerynknight.com",
    description=SHORT_DESCRIPTION[0:200],
    long_description=LONG_DESCRIPTION,
    packages=[
        "templateselector",
    ],
    include_package_data=True,
    install_requires=[
        "Django>=1.8",
    ] + INSTALL_REQUIRES,
    extras_require=EXTRA_REQUIRES,
    tests_require=[
        "pytest>=2.6",
        "pytest-django>=2.8.0",
        "pytest-cov>=1.8",
        "pytest-pythonpath>=0.7.1",
    ],
    cmdclass={"test": PyTest},
    zip_safe=False,
    keywords=" ".join(KEYWORDS),
    license=LICENSE,
    url=URL,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: {}".format(LICENSE),
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
    ],
)
