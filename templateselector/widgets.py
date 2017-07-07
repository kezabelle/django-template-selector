# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.forms import RadioSelect


__all__ = ['TemplateSelector', 'AdminTemplateSelector']


class TemplateSelector(RadioSelect):
    template_name = 'django/forms/widgets/template_selector.html'
    option_template_name = 'django/forms/widgets/template_selector_option.html'


    class Media:
        css = {
            'all': ('templateselector/widget.css',)
        }


class AdminTemplateSelector(TemplateSelector):
    def __init__(self, attrs=None):
        final_attrs = {'class': 'vTemplateSelectorField'}
        if attrs is not None:  # pragma: no cover
            final_attrs.update(attrs)
        super(AdminTemplateSelector, self).__init__(attrs=final_attrs)

    class Media:
        css = {
            'all': ('templateselector/admin_widget.css',)
        }
