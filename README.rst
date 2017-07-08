django-templateselector
=======================

:author: Keryn Knight
:version: 0.1.0

.. |travis_stable| image:: https://travis-ci.org/kezabelle/django-template-selector.svg?branch=0.1.0
  :target: https://travis-ci.org/kezabelle/django-template-selector

.. |travis_master| image:: https://travis-ci.org/kezabelle/django-template-selector.svg?branch=master
  :target: https://travis-ci.org/kezabelle/django-template-selector

==============  ======
Release         Status
==============  ======
stable (0.1.0)  |travis_stable|
master          |travis_master|
==============  ======


.. contents:: Sections
   :depth: 2

What it does
------------

Provides a new model field, ``fields.TemplateField`` which allows for selection
of a specific `Django`_ template using a nice form field (``fields.TemplateChoiceField``)
and a nicer widget (``widgets.TemplateSelector``) than the standard ``<select>`` dropdown.

Use case
--------

Imagine you have a ``Page`` model, and you want to allow admins or page authors
to choose from a range of templates for the page to use, you could do this::

  from django.dbimport models
  from templateselector.fields import TemplateField

  class MyPage(models.Model):
    title = models.CharField(max_length=100)
    # ...
    template = TemplateField(match='^myapp/mypage/layouts/.+\.html$')

which would allow them to select any HTML file Django could find in the
appropriate directory.


Available functionality
-----------------------

These fields are really the only public API. There's obviously other stuff, if you
care to rummage around.

``TemplateField``
^^^^^^^^^^^^^^^^^

Extends CharField, and requires a ``match`` argument which ought to be a
string version of a regular expression. The ``match`` will be used to filter
the possible choices. Optionally also takes a ``display_name`` argument, which
is a callable (or ``dotted.string.path.to.one``) that takes a given
string (the selected template path) and returns a nice name for it.
The default form field for ``TemplateField`` is ``TemplateChoiceField``

``TemplateChoiceField``
^^^^^^^^^^^^^^^^^^^^^^^

Has the same arguments as ``TemplateField``, and can be used independently
in all forms if you want to not use the model field.

``nice_display_name``
^^^^^^^^^^^^^^^^^^^^^

This function is the default callable for the ``display_name`` arguments on
the ``TemplateField`` and ``TemplateChoiceField``, it tries to provide some
flexibility and sensisble defaults; specifically:

* If your project defines a ``TEMPLATESELECTOR_DISPLAY_NAMES`` setting which
  is a dictionary like ``{'path/to/template.html': "my awesome template"}`` then
  the name ``"my awesome template"`` will be shown by preference.
* If not set, or no key match is found, the function will take the *file name*
  (not the path!) without *any extension* and will attempt to make a pretty, readable
  name of it by replacing most non-alphabet characters with spaces, so
  the template ``test/app/hello_world.html`` would become ``Hello World``

Supported Django versions
-------------------------

The tests are run against Django 1.11 on Python 2.7, and 3.5.
The widget uses the Django 1.11 template-based-rendering, so won't work on
previous versions.


Installation and usage
----------------------

This is currently only available via git ...

Installation
^^^^^^^^^^^^

Grab it from  `GitHub`_  like this::

  pip install -e git+https://github.com/kezabelle/django-template-selector.git#egg=django-template-selector

Configuration
^^^^^^^^^^^^^

To get the ``TemplateSelector`` widget to display correctly, you *will* need to
add ``templateselector`` to your project's ``INSTALLED_APPS``.

Running the tests
^^^^^^^^^^^^^^^^^

If you have a cloned copy, you can do::

  python setup.py test

If you have tox, you can just do::

  tox

Running the demo
^^^^^^^^^^^^^^^^

A barebones demo is provided. It assumes you're using something like `virtualenv`_ and
`virtualenvwrapper`_ but you can probably figure it out otherwise::

    mktmpenv --python=`which python3`
    pip install -e git+https://github.com/kezabelle/django-template-selector.git#egg=django-templateselector

Then probably::

    cd src/django-templateselector
    python demo_project.py runserver

The index page ``/`` will show you a normal version of the selection widget,
while ``/admin/tests/mymodel/add/`` will show the slightly customised version
for the standard `Django`_ admin.

The license
-----------

It's the `FreeBSD`_. There's should be a ``LICENSE`` file in the root of the repository, and in any archives.

.. _Django: https://www.djangoproject.com/
.. _GitHub: https://github.com/
.. _FreeBSD: http://en.wikipedia.org/wiki/BSD_licenses#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _virtualenv: https://virtualenv.pypa.io/en/stable/
