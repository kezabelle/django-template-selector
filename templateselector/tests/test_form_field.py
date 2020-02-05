# -*- coding: utf-8 -*-
from unittest import skipIf
from uuid import UUID

import django
import pytest

from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.forms import Form, IntegerField, modelform_factory
from django.test import override_settings, SimpleTestCase
from django.utils.encoding import force_text
from templateselector.fields import TemplateChoiceField
from templateselector.widgets import TemplateSelector, AdminTemplateSelector


@pytest.yield_fixture
def modelcls():
    from templateselector.tests.models import MyModel
    yield MyModel

def test_field_warns_if_providing_coerce_callable():
    with pytest.raises(ImproperlyConfigured):
        TemplateChoiceField(coerce=int, match=r"^.*$")

def test_field_warns_if_providing_dumb_display_name():
    with pytest.raises(ImproperlyConfigured):
        TemplateChoiceField(display_name='goose', match=r"^.*$")


def test_field_warns_if_missing_caret_at_start():
    with pytest.raises(ImproperlyConfigured):
        TemplateChoiceField(match=r".*$")


def test_field_warns_if_missing_dollar_at_end():
    with pytest.raises(ImproperlyConfigured):
        TemplateChoiceField(match=r"^.*")


def test_model_field_yields_correct_formfield(modelcls):
    x = modelcls()
    y = x._meta.get_field('f').formfield()
    assert isinstance(y, TemplateChoiceField)


@override_settings(TEMPLATESELECTOR_DISPLAY_NAMES={'admin/500.html': '500'})
def test_choices():
    x = TemplateChoiceField(match=r"^admin/[0-9]+.html$")
    assert set(x.choices) == {('admin/404.html', '404'), ('admin/500.html', '500')}


def test_choices_using_custom_setting_mapping():
    s = {
        'admin/404.html': 'Page Not Found',
        'admin/500.html': 'Server Error',
    }
    with override_settings(TEMPLATESELECTOR_DISPLAY_NAMES=s):
        x = TemplateChoiceField(match=r"^admin/[0-9]+.html$")
        assert set(x.choices) == set(s.items())


def test_choices_using_custom_namer():
    def namer(data):
        return str(UUID('F'*32))
    x = TemplateChoiceField(match=r"^admin/[0-9]+.html$", display_name=namer)
    assert set(x.choices) == {('admin/404.html', 'ffffffff-ffff-ffff-ffff-ffffffffffff'),
                              ('admin/500.html', 'ffffffff-ffff-ffff-ffff-ffffffffffff')}


@pytest.fixture
def form_cls():
    class MyForm(Form):
        a = IntegerField()
        b = TemplateChoiceField(match=r"^admin/[0-9]+.html$")
    return MyForm


def test_form_usage_invalid(form_cls):
    f = form_cls(data={'a': '1', 'b': 'goose'})
    assert f.is_valid() is False
    assert f.errors == {'b': ['Select a valid choice. goose is not one of the available choices.']}

def test_form_usage_ok(form_cls):
    f = form_cls(data={'a': '1', 'b': 'admin/404.html'})
    assert f.is_valid() is True
    assert f.errors == {}


def test_admin_default_formfield(rf, modelcls):
    modeladmin = admin.site._registry[modelcls]
    request = rf.get('/')
    form = modeladmin.get_form(request=request)()
    widget = form.fields['f'].widget
    assert isinstance(widget, TemplateSelector)
    assert isinstance(widget, AdminTemplateSelector)


def test_html_output(form_cls):
    form = form_cls(data={'a': '1', 'b': 'admin/404.html'})
    STATIC_URL = "/TESTOUTPUT/"
    with override_settings(STATIC_URL=STATIC_URL, TEMPLATESELECTOR_DISPLAY_NAMES={'admin/500.html': '500'}):
        rendered = force_text(form['b'])

    SimpleTestCase().assertHTMLEqual(rendered, """
<ul id="id_b" class="templateselector-list ">
    <li class="templateselector-list-item">
        <label  for="id_b_0" class="templateselector-label">
        <input type="radio" name="b" value="admin/404.html" required id="id_b_0" checked />

        <span class="templateselector-thumb" style="background-image: url('{STATIC_URL}admin/404.html.png'), url('{STATIC_URL}templateselector/fallback.png');"></span>
        <span class="templateselector-display-name">404</span>
        </label>
    </li>
    <li class="templateselector-list-item">
        <label  for="id_b_1" class="templateselector-label">
        <input type="radio" name="b" value="admin/500.html" required id="id_b_1" />

        <span class="templateselector-thumb" style="background-image: url('{STATIC_URL}admin/500.html.png'), url('{STATIC_URL}templateselector/fallback.png');"></span>
        <span class="templateselector-display-name">500</span>
        </label>
    </li>
</ul>
        """.format(STATIC_URL=STATIC_URL))


def test_pre_selecting_happns_if_only_one_choice_and_required_unbound():
    class MyForm(Form):
        field = TemplateChoiceField(
            match=r"^django/forms/widgets/template_selector.html$",
            required=True)

    form = MyForm(data=None)
    rendered = force_text(form['field'])
    SimpleTestCase().assertInHTML('<input type="radio" name="field" value="django/forms/widgets/template_selector.html" required checked id="id_field_0" />', rendered, count=1)

def test_no_pre_selecting_occurs_for_more_than_one_choice():
    class MyForm(Form):
        field = TemplateChoiceField(
            match=r"^django/forms/widgets/template_.+\.html$",
            required=True)

    form = MyForm(data=None)
    rendered = force_text(form['field'])
    SimpleTestCase().assertInHTML('<input type="radio" name="field" value="django/forms/widgets/template_selector.html" required id="id_field_0" />', rendered, count=1)
    SimpleTestCase().assertInHTML('<input type="radio" name="field" value="django/forms/widgets/template_selector_option.html" required id="id_field_1" />', rendered, count=1)

def test_no_pre_selecting_if_field_is_not_required():
    class MyForm(Form):
        field = TemplateChoiceField(
            match=r"^django/forms/widgets/template_selector.html$",
            required=False)

    form = MyForm(data=None)
    rendered = force_text(form['field'])
    SimpleTestCase().assertInHTML('<input type="radio" name="field" value="django/forms/widgets/template_selector.html" id="id_field_0" />', rendered, count=1)

def test_no_pre_selecting_happens_for_bound_forms():
    class MyForm(Form):
        field = TemplateChoiceField(
            match=r"^django/forms/widgets/template_.+\.html$",
            required=False)

    form = MyForm(data={'field': 'django/forms/widgets/template_selector_option.html'})
    rendered = force_text(form['field'])
    SimpleTestCase().assertInHTML('<input type="radio" name="field" value="django/forms/widgets/template_selector.html" id="id_field_0" />', rendered, count=1)
    SimpleTestCase().assertInHTML('<input type="radio" name="field" value="django/forms/widgets/template_selector_option.html" checked id="id_field_1" />', rendered, count=1)


def test_no_duplicates():
    field = TemplateChoiceField(match=r"^django/forms/widgets/template_.+\.html$")
    assert list(field.choices) == [
        (u'django/forms/widgets/template_selector.html', u'Template selector'),
        (u'django/forms/widgets/template_selector_option.html', u'Template selector option'),
    ]


def test_form_validation_supercedes_model_validation_when_used_together(rf, modelcls):
    request = rf.get('/', data={
        'f': 'admin/should_not_exist.json'
    })
    Form = modelform_factory(modelcls, fields=['f'])
    form = Form(data=request.GET)
    assert form.is_valid() is False
    assert form.errors == {
        'f': ['Select a valid choice. admin/should_not_exist.json is not one of the available choices.']
    }
