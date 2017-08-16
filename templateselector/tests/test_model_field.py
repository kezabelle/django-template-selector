# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest
from django.contrib.admin import ModelAdmin, AdminSite
from django.contrib.admin.templatetags.admin_list import result_headers
from django.contrib.admin.views.main import ChangeList

from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.template.backends.django import Template
from django.test import override_settings
from templateselector.admin import TemplateFieldListFilter
from templateselector.fields import TemplateField


@pytest.yield_fixture
def modelcls():
    from templateselector.tests.models import MyModel
    yield MyModel


@pytest.yield_fixture
def modelclsadmin(modelcls):
    class MyChangeList(ChangeList):
        def get_results(self, request):
            return 0
    class MyModelAdmin(ModelAdmin):
        list_display = ("pk", "f",)
        list_filter = ("f",)
        def get_changelist(self, request, **kwargs):
            return MyChangeList
    modeladmin = MyModelAdmin(model=modelcls, admin_site=AdminSite())
    yield modeladmin

@pytest.yield_fixture
def modelclschangelist(rf, modelclsadmin):
    request = rf.get('/')
    cl_cls = modelclsadmin.get_changelist(request=request)
    cl = cl_cls(request=request, model=modelclsadmin.model,
                list_display=modelclsadmin.list_display,
                list_display_links=(), list_filter=modelclsadmin.list_filter,
                date_hierarchy=None, search_fields=None,
                list_select_related=False, list_per_page=5,
                list_max_show_all=5, list_editable=(),
                model_admin=modelclsadmin)
    yield cl


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


def test_admin_order_field_attr(modelcls):
    curried = modelcls(f="admin/index.html").get_f_display
    assert curried.admin_order_field == "f"


def test_admin_order_field_changelist(rf, modelclschangelist):
    result = modelclschangelist.get_ordering_field("get_f_display")
    assert result == "f"


def test_admin_order_field_result_headers_templatetag(modelclschangelist):
    results = tuple(result_headers(cl=modelclschangelist))
    assert len(results) == 2
    assert results[1]['sortable'] is True


@pytest.mark.django_db
def test_admin_filter_used(rf, modelcls, modelclschangelist):
    request = rf.get('/')
    result = modelclschangelist.get_filters(request=request)
    assert result[1] is True
    assert len(result[0]) == 1
    assert isinstance(result[0][0], TemplateFieldListFilter)


@pytest.mark.django_db
def test_admin_filter_lists_correct_values(rf, modelcls, modelclschangelist):
    request = rf.get('/')
    result = modelclschangelist.get_filters(request=request)
    obj = modelcls(f="admin/index.html")
    obj.full_clean()
    obj.save()
    with override_settings(TEMPLATESELECTOR_DISPLAY_NAMES={"admin/index.html": "GOOSE!"}):
        choices = tuple(result[0][0].choices(modelclschangelist))
    displays = tuple(x['display'] for x in choices)
    assert displays == ('All', 'GOOSE!')
