# -*- coding: utf-8 -*-
from django.db.models import Model
from django.utils.encoding import force_text
from templateselector.fields import TemplateField

class MyModel(Model):
    f = TemplateField(match="^admin/.+\.html$", verbose_name="test 'f'")

    def __str__(self):
        return force_text(self.pk)
