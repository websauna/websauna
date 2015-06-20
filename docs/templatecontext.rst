
Template variables
==================

The following variables are available in the templates, as set by :py:mod:`websauna.system.core.templatecontext`.

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

