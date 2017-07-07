# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest

from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.template.backends.django import Template
from templateselector.fields import TemplateField


@pytest.yield_fixture
def modelcls():
    from templateselector.tests.models import MyModel
    yield MyModel


def test_field_maxlength(modelcls):
    x = modelcls()
    assert x._meta.get_field('f').max_length == 191


def test_field_warns_if_providing_maxlength():
    with pytest.raises(ImproperlyConfigured):
        TemplateField(max_length=3, match="")


def test_field_warns_if_providing_dumb_display_name():
    with pytest.raises(ImproperlyConfigured):
        TemplateField(display_name='goose', match="^.*$")


def test_template_exists(modelcls):
    x = modelcls(f="admin/index.html")
    x.full_clean()

def test_template_does_not_exist_cleaning_errors(modelcls):
    x = modelcls(f="admin/in2dex.html")
    with pytest.raises(ValidationError):
        x.full_clean()


def test_template_instance_function_exists(modelcls):
    x = modelcls(f="admin/index.html")
    y = x.get_f_instance()
    assert isinstance(y, Template)


def test_template_instance_function_doesnt_swallow_exception(modelcls):
    x = modelcls(f="admin/ind2ex.html")
    with pytest.raises(TemplateDoesNotExist):
        x.get_f_instance()


def test_template_display_name(modelcls):
    x = modelcls(f="admin/index.html")
    y = x.get_f_display()
    assert y == 'Index'
