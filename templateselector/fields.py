# -*- coding: utf-8 -*-
from operator import itemgetter
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles import finders
from django.utils.deconstruct import deconstructible
from django.utils.module_loading import import_string
from django.utils.text import capfirst
from django.core.checks import Warning
from templateselector.handlers import get_results_from_registry
from templateselector.widgets import TemplateSelector, AdminTemplateSelector
import re
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import MaxLengthValidator
from django.db.models import CharField
from django.forms import TypedChoiceField
from django.template import TemplateDoesNotExist, engines
from django.template.loader import get_template
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _


__all__ = ['TemplateField', 'TemplateChoiceField']


def get_templates_from_loaders():
    for engine in engines.all():
        # I only know how to search the DjangoTemplates yo...
        engine = getattr(engine, 'engine')
        loaders = engine.template_loaders
        for result in get_results_from_registry(loaders):
            yield result


def nice_display_name(template_path):
    setting = getattr(settings, 'TEMPLATESELECTOR_DISPLAY_NAMES', {})
    if template_path in setting.keys():
        return setting[template_path]
    to_space_re = re.compile(r'[^a-zA-Z0-9\-]+')
    name = template_path.rpartition('/')[-1]
    basename = name.rpartition('.')[0]
    lastpart_spaces = to_space_re.sub(' ', basename)
    return capfirst(_(lastpart_spaces))


@deconstructible
class TemplateExistsValidator(object):
    __slots__ = ('regex', 'missing_template', 'wrong_pattern', '_constructor_args')
    def __init__(self, regex):
        self.regex = re.compile(regex)
        self.missing_template = _('%(value)s is not a valid template')
        self.wrong_pattern = _("%(value)s doesn't match the available template format")

    def __call__(self, value):
        if not self.regex.match(value):
            raise ValidationError(self.wrong_pattern, params={'value': value})
        try:
            get_template(value)
        except TemplateDoesNotExist:
            raise ValidationError(self.missing_template, params={'value': value})


class TemplateField(CharField):
    def __init__(self, match='^.*$', display_name='templateselector.fields.nice_display_name', *args, **kwargs):
        if 'max_length' in kwargs:
            raise ImproperlyConfigured(_("max_length is implicitly set to 191 internally"))
        kwargs['max_length'] = 191 # in case of using mysql+utf8mb4 & indexing
        super(TemplateField, self).__init__(*args, **kwargs)

        if not match.startswith('^'):
            raise ImproperlyConfigured("Missing required ^ at start")
        if not match.endswith('$'):
            raise ImproperlyConfigured("Missing required $ at end")
        self.match = match
        template_exists_validator = TemplateExistsValidator(self.match)
        self.validators.append(template_exists_validator)

        if isinstance(display_name, str) and '.' in display_name:
            display_name = import_string(display_name)
        if not callable(display_name):
            raise ImproperlyConfigured(_("display_name= argument must be a callable which takes a single string"))
        self.display_name = display_name

    def deconstruct(self):
        name, path, args, kwargs = super(TemplateField, self).deconstruct()
        del kwargs["max_length"]
        kwargs['match'] = self.match
        kwargs['display_name'] = self.display_name
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': TemplateChoiceField,
            'match': self.match,
            'display_name': self.display_name,
        }
        defaults.update(kwargs)
        return super(TemplateField, self).formfield(**defaults)

    def check(self, **kwargs):
        errors = []
        templates = (
            'django/forms/widgets/template_selector.html',
            'django/forms/widgets/template_selector_option.html'
        )
        missing = set()
        for t in templates:
            try:
                get_template('django/forms/widgets/template_selector.html')
            except TemplateDoesNotExist:
                missing.add(t)
        if missing:
            msg = "Could not load templates: {}".format(missing)
            hint = ("Add 'templateselector' to your INSTALLED_APPS,\n\t      "
                    "OR create the templates yourself,\n\t      "
                    "OR silence this warning and don't use the default TemplateSelector widget")
            errors.append(
                Warning(msg, hint=hint, obj=self, id='templateselector.W001')
            )
        css_files = (
            'templateselector/widget.css',
            'templateselector/admin_widget.css',
        )
        css_missing = set()
        for css in css_files:
            css_file = finders.find(css)
            if css_file is None:
                css_missing.add(css)
        if css_missing:
            msg = "Could not load staticfiles: {}".format(css_missing)
            hint = ("Add 'templateselector' to your INSTALLED_APPS\n\t      "
                    "OR create the file and necessary styles yourself")
            errors.append(
                Warning(msg, hint=hint, obj=self, id='templateselector.W002')
            )
        return errors

    def contribute_to_class(self, cls, name, **kwargs):
        super(TemplateField, self).contribute_to_class(cls, name, **kwargs)
        field = self
        def __get_FIELD_template_display(self):
            value = getattr(self, field.attname)
            return field.display_name(value)
        def __get_FIELD_template_instance(self):
            value = getattr(self, field.attname)
            return get_template(value)
        __get_FIELD_template_display.short_description = self.verbose_name
        __get_FIELD_template_display.admin_order_field = name
        setattr(cls, 'get_%s_display' % self.name, __get_FIELD_template_display)
        setattr(cls, 'get_%s_instance' % self.name, __get_FIELD_template_instance)


class TemplateChoiceField(TypedChoiceField):
    widget = TemplateSelector

    def __init__(self, match='^.*$', display_name='templateselector.fields.nice_display_name', *args, **kwargs):
        if 'coerce' in kwargs:
            raise ImproperlyConfigured(_("Don't pass a coercion callable"))
        kwargs['coerce'] = force_text
        max_length = None
        if 'max_length' in kwargs:
            max_length = kwargs.pop('max_length')
        if isinstance(display_name, str) and '.' in display_name:
            display_name = import_string(display_name)
        if not callable(display_name):
            raise ImproperlyConfigured(_("display_name= argument must be a callable which takes a single string"))
        super(TemplateChoiceField, self).__init__(*args, **kwargs)

        if not match.startswith('^'):
            raise ImproperlyConfigured("Missing required ^ at start")
        if not match.endswith('$'):
            raise ImproperlyConfigured("Missing required $ at end")

        def lazysorted():
            def filter_choices(regex_, namecaller_):
                match_re = re.compile(regex_)
                choices = get_templates_from_loaders()
                for choice in choices:
                    if match_re.match(choice):
                        name = namecaller_(choice)
                        yield (choice, name)
            results = filter_choices(regex_=match, namecaller_=display_name)
            return sorted(set(results), key=itemgetter(1))

        self.choices = lazysorted
        self.max_length = max_length
        if max_length is not None:
            self.validators.append(MaxLengthValidator(int(max_length)))

    def prepare_value(self, value):
        """
        To avoid evaluating the lazysorted callable more than necessary to
        establish a potential initial value for the field, we do it here.

        If there's
        - only one template choice, and
        - the field is required, and
        - there's no prior initial set (either by being bound or by being set
          higher up the stack
        then forcibly select the only "good" value as the default.
        """
        if value is None and self.required:
            choices =list(self.choices)
            if len(choices) == 1:
                value = choices[0][0]
        return super(TemplateChoiceField, self).prepare_value(value)


# It doesn't matter wtf the formfield() method for our custom model field says
# because the admin looks at the MRO for the model field and tries to render
# it as a bloody text input.
admin.options.FORMFIELD_FOR_DBFIELD_DEFAULTS[TemplateField] = {'widget': AdminTemplateSelector}
