=========================
Automatic form generation
=========================

Websauna comes with an automatic form generator for :term:`SQLAlchemy` models.

.. contents:: :local:

* :term:`Colander` form schema can be generated with :term:`Deform` widgets from :term:`SQLAlchemy` models automatically based on field mapper (:py:class:`websauna.system.form.fieldmapper.DefaultFieldMapper`).

* :doc:`Automatically generated model admin interface <../crud/admin>` use this.

* :doc:`CRUD implementation can be used standalone <../crud/crud>` from the admin interface, e.g. inside user profile or other user facing pages.

An example of automatically generated form - the question edit page from :doc:`the tutorial <../../tutorials/gettingstarted/index>`:

.. image:: ../../tutorials/gettingstarted/images/edit_question.png
    :width: 640px

Form generation
===============

The core part of form generation is :py:meth:`websauna.system.form.fieldmapper.ColumnToFieldMapper` which maps SQLAlchemy columns to Colander schema.

See :py:meth:`websauna.system.form.fieldmapper.DefaultFieldMapper.map` for interface.

See :py:meth:`websauna.system.crud.views.FormView.create_form` for a usage example how to call the field mapper.

See classes in :py:mod:`websauna.system.user.adminviews` for examples how to customize automatically included fields.

Internally form generation uses highly modified :term:`colanderalchemy` library.

.. note::

    Due to high customization this dependency is likely to go away.

Customizing automatically generated forms
=========================================

There are several ways to customize automatic form generation based on your use case.

Edit includes attribute
-----------------------

This is the most common way to customize :doc:`CRUD <../crud/crud>` forms. Each CRUD class comes with ``includes`` attribute which lists fields which are pulled from the SQLAlchemy columns, or other Python object properties, to a form.

* :py:class:`websauna.system.crud.views.Add`

* :py:class:`websauna.system.crud.views.Edit`

* :py:class:`websauna.system.crud.views.Show`

Edit :py:meth:`websauna.system.crud.views.FormView.includes` attribute to include the list of fields to include. This list can contain

* ``string``: String presents a name of a column that goes to form. You can omit the names of the columns you don't want to show on the form.

* :py:class:`colander.SchemaNode` - add custom field and customize widgets for existing columns. Rememeber to have ``name`` attribute matching to a column.

Example:

.. code-block:: python

    import colander

    from websauna.system.admin import views as admin_views
    from websauna.system.form.fields import defer_widget_values
    from websauna.system.user.schemas import group_vocabulary
    from websauna.system.user.schemas import GroupSet

     class UserEdit(admin_views.Edit):
        """Edit one user."""

        includes = admin_views.Edit.includes + [
                    "enabled",
                    colander.SchemaNode(colander.String(), name='username'),  # Make username required field
                    colander.SchemaNode(colander.String(), name='full_name', missing=""),
                    "email",
                    colander.SchemaNode(GroupSet(), name="groups", widget=defer_widget_values(deform.widget.CheckboxChoiceWidget, group_vocabulary, css_class="groups"))
                    ]


Subclass CRUD view and override customize_schema
------------------------------------------------

This applies for automatic :term:`CRUD`.

Subclass your form from

* :py:class:`websauna.system.crud.views.Add`

* :py:class:`websauna.system.crud.views.Edit`

* :py:class:`websauna.system.crud.views.Show`

Override :py:meth:`websauna.system.crud.views.FormView.customize_schema` to edit generated :py:class:`colander.SchemaNode` in place.

Example:

.. code-block:: python

    from websauna.system.crud.views import Add
    from websauna.system.core.viewconfig import view_overrides

    # This view applies to imaginary CommentCRUD which manages SQLAlchemy Comment model
    @view_overrides(context=CommentCRUD)
    class MyView(Add):

        def customize_schema(self, schema):
            if request.user:
                # Do nothing, we know the name of the logged in user already
                pass
            else:
                rating.add(colander.SchemaNode(colander.String(), label="Leave your name for feedback", name="anonymous_visitor_name", missing="", widget=deform.widget.TextInputWidget()))

Rolling out your own view with field mapper
-------------------------------------------

You can also write everything from scratch and call field mapper.

Example:

.. code-block:: python

    from uuid import UUID

    from pyramid.httpexceptions import HTTPFound
    from websauna.system.core import messages
    from websauna.system.http import Request
    from websauna.system.form.fieldmapper import EditMode
    from websauna.system.form.csrf import add_csrf
    from websauna.system.core.route import simple_route
    from websauna.utils.slug import slug_to_uuid


    from myapp.model import Question


    @simple_route("/edit_question/{question_uuid}",
                  route_name="edit_question",
                  renderer="myapp/edit_question.html",)
    def detail(request: Request):
        # Convert base64 encoded UUID string from request path to Python UUID object
        question_uuid = slug_to_uuid(request.matchdict["question_uuid"])

        question = request.dbsession.query(Question).filter_by(uuid=question_uuid).first()
        if not question:
            raise HTTPNotFound()



        # Generate a form from SQLAlchemy model
        # includes not set -> include all fields on SQLALchemy model
        schema = self.field_mapper.map(EditMode.add, request, None, Question, includes=None, nested=nested)

        # In this point use schema.add(), schema["question_text"], e.g. to edit the schema

        # Make sure we have CSRF token as a hidden field
        add_csrf(schema)

        schema = self.bind_schema(schema, request=request)

        if request.method == "POST":

            controls = self.request.POST.items()

            try:
                appstruct = form.validate(controls)

                # Validation passed -> edit obj
                question.question_text = appstruct["question_text"]
                question.published_at = appstruct["published_at"]
                messages.add(kind="success", msg_id="question-edit-saved", "Your edit was saved")
                return HttpFound(request.route_url("home"))

            except deform.ValidationFailure as e:
                # Whoops, bad things happened, render form with validation errors
                rendered_form = e.render()
        else:
            rendered_form = form.render()

        # Load widget CSS/JS
        form.resource_registry.pull_in_resources(request, form)

        return locals()


See also :py:class:`websauna.system.crud.views.FormView.create_form`.

Override field_mapper attribute
-------------------------------

Inherit from a crud view and override :py:attr:`websauna.system.crud.views.FormView.field_mapper` with your own instance of :py:class:`websauna.system.form.fieldmapper.ColumnToFieldMapper`.

