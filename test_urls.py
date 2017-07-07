# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.conf.urls import url, include
from django.contrib import admin
from django.forms import Form
from django.http import HttpResponse
from django.template import Template, Context
from templateselector.fields import TemplateChoiceField


def example(request):
    class MyForm(Form):
        field = TemplateChoiceField(match="^admin/[0-9]+.html$")
    context = {
        'form': MyForm(request.GET or None),
    }
    template = Template("""
    <!DOCTYPE html>
    <html>
    <head>{{ form.media }}</head>
    <body>
    <form action="" method="GET">
    {{ form.media }}
    {{ form.field }}
    <input type="submit" value="Click!">
    </form>
    </body>
    </html>
    """)
    return HttpResponse(template.render(Context(context)))

urlpatterns = [
    url('^admin/', include(admin.site.urls)),
    url('^$', example),
]

import debug_toolbar
urlpatterns = [
    url(r'^__debug__/', include(debug_toolbar.urls)),
] + urlpatterns
