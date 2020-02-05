# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.forms import Form
from django.http import HttpResponse
from django.template import Template, Context
from templateselector.fields import TemplateChoiceField


def example(request):
    class MyForm1(Form):
        field = TemplateChoiceField(match="^admin/[0-9]+.html$")

    class MyForm2(Form):
        field = TemplateChoiceField(match="^admin/404.html$")

    class MyForm3(Form):
        field = TemplateChoiceField(match="^admin/_doesnt_exist_.html$")

    context = {
        'forms': (
            MyForm1(request.GET or None, prefix='form1'),
            MyForm2(request.GET or None, prefix='form2'),
            MyForm3(request.GET or None, prefix='form3'),
        )
    }
    template = Template("""<!DOCTYPE html>
    <html><head>
    <title>django-templateselector</title>
    {{ forms.0.media }}</head>
    <body>
    <form action="" method="GET" accept-charset="utf-8">
    {% for form in forms %}
    <div style="background-color: #FFF; border-bottom: 1px solid #DDD; padding: 1rem;">
    {{ form.field }}
    {{ form.field.errors }}
    </div>
    {% endfor %}
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
try:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
except ImportError:
    pass
