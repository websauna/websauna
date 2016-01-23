================
Template context
================

.. contents:: :local:

Variables
=========

The following variables are available in the templates, as set by :py:mod:`websauna.system.core.templatecontext`.

Filters
=======

.. _static_url:

static_url
----------

Refer to a static asset inside a Python package.

Example::

    <img src="{{ 'myapp:static/logo.png'|static_url }}" alt="">

Provided by :term`pyramid_jinja2` package.

Other template context
======================

Permission checks
-----------------

Use :py:meth:`pyramid.request.Request.has_permission` to check if the user has the named permission in the current context.

Example: checking if the user has a permission on certain model admin functions inside admin panel template::

    {% block panel_buttons %}

        {% if request.has_permission('view', context) %}
            <a id="btn-panel-list-{{ model_admin.id }}" class="btn btn-default btn-admin-list" href="{{ model_admin|model_url('listing') }}">
                List
            </a>
        {% endif %}


        {% if request.has_permission('add', context) %}
            <a id="btn-panel-add-{{ model_admin.id }}" class="btn btn-default btn-admin-list" href="{{ model_admin|model_url('add') }}">
                Add
            </a>
        {% endif %}
    {% endblock %}

Site root context
------------------

Use :py:meth:`pyramid.request.Request.root`.

