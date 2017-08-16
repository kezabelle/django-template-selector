# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.contrib.admin import AllValuesFieldListFilter, FieldListFilter
from django.utils.translation import ugettext_lazy as _


_ALL = _('All')


class TemplateFieldListFilter(AllValuesFieldListFilter):
    def choices(self, changelist):
        for choice in super(TemplateFieldListFilter, self).choices(changelist=changelist):
            if choice['display'] == _ALL:
                yield choice
            else:
                choice['display'] = self.field.display_name(choice['display'])
                yield choice

from templateselector.fields import TemplateField
FieldListFilter.register(lambda f: isinstance(f, TemplateField),
                         TemplateFieldListFilter, take_priority=True)
