# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin
from templateselector.tests.models import MyModel


class MyModelAdmin(admin.ModelAdmin):
    list_display = ("__unicode__", "get_f_display")
admin.site.register(MyModel, MyModelAdmin)
