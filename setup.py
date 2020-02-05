#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand

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
    version="1.0.0",
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
        "Django>=2.0",
    ],
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
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Django :: 2",
        "Framework :: Django :: 3",
    ],
)
