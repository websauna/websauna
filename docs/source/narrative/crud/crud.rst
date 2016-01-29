====
CRUD
====

Introduction
============

Websauna comes with :term:`CRUD` which allows you to build create-read-update-delete user interfaces easily for your models.

* CRUD comes with built-in support :term:`SQLAlchemy` models, but can be used any kind of model library or databaes

* CRUD supports :doc:`form autogeneration <../form/autoform>`, so that a CRUD UI can be generated automatically from SQLAlchemy models. You do not need to write each form by hand.

* CRUD is abstract and supports plugging in other data sources besides SQLAlchemy (see :py:class:`websauna.system.crud.CRUD` and :py:class:`websauna.system.crud.sqlalchemy.CRUD`).

* CRUD is extensively used by model :ref:`admin` interface

CRUD elements
=============

CRUD consists of basic views which are

* List all items

* Add item (C) - a form based view

* Show item (R) - a form based view

* Edit item (U) - a form based view

* Delete item (D)

CRUD controller is :term:`traversal` based and thus can be plugged in to any part of the site without a hardcoded URL configuration.

You need do

* Declare one subclass of `websauna.system.crud.CRUD` which servers the entry point into your CRUD

* This class must contain inner class of subclass of `websauna.system.crud.CRUD.Resource` which wraps raw SQLAlchemy object to traversable URLs

After this you can override any of the views by subclassing the base view and customizing it for your purposes.

For example here is an URL from the tutorial::

    http://localhost:6543/admin/models/choice/zYkpKEkpSvq02tPjL_ko8Q/show

Below is how CRUD is formed. It consists of four :term:`resource` classes (see :py:class`websauna.system.core.traversal.Resource`) and one :term:`view`.

* ``admin`` is the default admin interface root of the site, see :py:class:`websauna.system.admin.admin.Admin`

* ``admin`` contains ``models`` path under which all CRUDs for models registered for admin are. This is presented by :py:class:`websauna.system.admin.modeladmin.ModelAdminRoot`

* ``choices`` is a CRUD root for Choices :term:`SQLAlchemy` :term:`model`. It is presented by ``myapp.admins.Choice`` which is a subclass of ``websauna.system.admin.modeladmin.ModelAdmin`` which in turn is subclass of :py:class:`websauna.system.crud.sqlalchemy.CRUD` which is the subclass of abstract CRUD implementation :py:class:`websauna.system.crud.CRUD`

* ``zYkpKEkpSvq02tPjL_ko8Q`` is the base64 encoded ::term:`UUID` (see :py:func:`websauna.system.utils.slug.uuid_to_slug`) of the ``myapp.admins.Choice`` we are currently manipulating. It resolves to ``myapp.admins.Choice.Resource`` class which is the subclass of :py:class:`websauna.system.crud.sqlachemy.Resource``. This resource wraps one SQLAlchemy object to URL traversing by giving it ``__parent__`` pointer and ``__name__`` string. URL to SQLAlchemy item mapping is done by :py:class:`websauna.system.crud.urlmapper.Base64UUIDMapper`.

* ``show`` is the :term:`view` name. Views are picked against the context they are registered. Here the context is ``myapp.admins.Choice.Resource``. It maps to :py:class:`websauna.system.admin.views.Show`, subclass of :py:class:`websauna.system.crud.views.Show`.

* View processing starts when Pyramid router calls :py:meth:`websauna.system.crud.views.Show.show`.

URL mapping
-----------

CRUD provides translation of SQLAlchemy object ids to URL paths and vice versa.

* :py:class:`websauna.system.crud.urlmapper.Base64UUIDMapper` is recommended as it generates non-guessable URLs. It reads :term:`UUID` attribute from model and constructs Base64 encoded string of it.

* :py:class:`websauna.system.crud.urlmapper.IdMapper` can be used if you want to have primary keys directly in URLs.

* The behavior can be configured by setting :py:attr:`websauna.system.crud.CRUD.mapper` for your CRUD class.

The default behavior is to read ``uuid`` attribute and do base64 encoding for it:

.. code-block:: python

    from websauna.system.crud import Base64UUIDMapper

    class CRUD(_Resource):
        mapper = Base64UUIDMapper(mapping_attribute="uuid")


You can change the name of the attribute. For example if your model has UUID based primary key ``id`` and doesn't have a separate ``uuid`` attribute:

.. code-block:: python

    from websauna.system.admin.modeladmin import ModelAdmin, model_admin

    from .models import UserOwnedAccount
    from websauna.system.crud import Base64UUIDMapper

    @model_admin(traverse_id="user-accounts")
    class UserAccountAdmin(ModelAdmin):
        """Manage user owned accounts and their balances."""

        model = UserOwnedAccount
        mapper = Base64UUIDMapper(mapping_attribute="id")



Form schema generation
----------------------

*Show*, *edit* and *add* views have a form schema which describes how individual object is shown or edited. Form schema uses :doc`form autogeneration <../form/autoform>`, though you can manually specify the schema.

Form creation process is following for CRUDs manageing SQLAlchemy based data

* :py:meth:`websauna.system.crud.view.FormView.create_form` is called by subclasses.

* It reads :py:attr:`websauna.system.crud.view.FormView.form_generator` attribute. This attribute is unset in CRUD core xlasses. Admin classes like :py:class:`websauna.system.admin.adminviews.Show` point this to :py:class:`websauna.system.crud.formgenerator.SQLAlchemyFormGenerator`. You can also wire this to return a manually constured :py:class:`deform.Form` object directly.

* CRUD view exposes the model it manages through :py:meth:`websauna.system.crud.views.FormView.get_model` call. By default it takes the model from the current context object

* ``SQLAlchemyFormGenerator`` takes a parameter, ``includes``, which is the list of columns names or :py:class:`colander.SchemaNode` objects that go to the autogenerated form.

* :py:meth:`websauna.system.crud.formgenerator.SQLAlchemyFormGenerator.generate_form` takes in model class, :py:class:`websauna.system.form.editmode.EditMode` and passes them forward to underlying :py:class:`websauna.system.form.fieldmapper.DefaultSQLAlchemyFieldMapper`. This will run complex heurestics to determine which column generates which field and adjust widget parameters.

* ``websauna.system.crud.formgenerator.SQLAlchemyFormGenerator`` takes also a parameter ``schema_customizer`` which is a callback to edit generated form schema after its generation.

* ``websauna.system.crud.formgenerator.SQLAlchemyFormGenerator`` takes also a parameter ``schema_binder`` which is a callback to perform a `Colander schema bind <http://docs.pylonsproject.org/projects/colander/en/latest/binding.html>`_. This is how your forms can obtain information during the run-time (from database, from HTTP request). By defaul the binding is::

    schema.bind(request=request, context=context)

Example schema declaration (:py:class:`websauna.system.useradmin.adminviews.UserEdit):

.. code-block:: python

    import colander
    from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator

    class UserEdit(admin_views.Edit):
        """Edit one user in admin interface."""

        includes = [

            # Simple mapping by column name
            "enabled",

            # Use colander.SchemaNode to directly declare schema + its widget
            colander.SchemaNode(colander.String(), name='username'),

            colander.SchemaNode(colander.String(), name='full_name', missing=""),

            "email",

            # Widget creation must be deferred, because we don't know the Group class
            # and list of possible user groups until run-time
            colander.SchemaNode(GroupSet(),
                name="groups",
                widget=defer_widget_values(deform.widget.CheckboxChoiceWidget,
                    group_vocabulary,
                    css_class="groups"))
            ]

        # Create a form generator instance which will perform
        # creation of deform.Form during run-time
        form_generator = SQLAlchemyFormGenerator(includes=includes)

Permissions
-----------

CRUD uses :term:`Pyramid` :term:`ACL` to control what actions a user can perform.

* Listing and show views are controlled by permission ``view``

* Add view is controlled by permission ``add``

* Edit view is controlled by permission ``edit``

* Delete view is controlled by permission ``delete``

Below is a custom permission set up::

    from pyramid.security import Deny, Allow, Everyone

    from websauna.system.admin.modeladmin import ModelAdmin, model_admin

    from .models import UserOwnedAccount

    @model_admin(traverse_id="user-accounts")
    class UserAccountAdmin(ModelAdmin):
        """Manage user owned accounts and their balances."""

        model = UserOwnedAccount

        # Set permissions so that this information can be only shown,
        # never edited or deleted
        __acl__ = {
            (Deny, Everyone, 'add'),
            (Allow, 'group:admin', 'view'),
            (Deny, Everyone, 'edit'),
            (Deny, Everyone, 'delete'),
        }

When rendering links and buttons CRUD templates check the permissions, so that elements are hidden if the user cannot perform the target action:

.. code-block:: html+jinja

    {# Instance is subclass of websauna.system.CRUD.Resource #}
    {% if request.has_permission("view", instance) %}
        <a href="{{ instance|resource_url('show') }}">
            Show
        </a>
    {% endif %}

Listing view
============

Listing view is provided by :py:class:`websauna.system.crud.views.Listing`. It uses ``Table`` and various ``Column`` classes in :py:mod:`websauna.system.crud.listing` to describe how the listing looks like.

* The context of a listing view is :py:class:`websauna.system.crud.CRUD`

* For an example listing view, see :ref:`overriding listing view in admin example <override-listing>`.

* Stock user listing view py:class:`websauna.system.user.adminviews.UserListing`

* Listing reads the data for the list by setting up and iterating a query coming from :py:meth:`websauna.system.crud.CRUD.get_query`

Add view
========

Add view is responsible for creating new items in the crud. It is a form based view and uses form autogeneration to create a new form.

* The context of a add view is :py:class:`websauna.system.crud.CRUD` or its subclasses

* For example, see :py:class:`websauna.system.user.adminviews.UserAdd`

* Availability of *Add* button in CRUD is controlled by permissions ``add``

Customizing created objects
---------------------------

Override ``create_object()``. Example:

.. code-block:: python

    @view_overrides(context=ReferralProgramAdmin)
    class ReferralProgramAdd(adminviews.Add):
        """Admin view for editing shortened URL."""

        # We only ask for name field, everything else is filled by system
        includes = [
            "name"
        ]

        def create_object(self):
            """When created through admin, all referral programs are internal type by default."""
            model = self.get_model()
            item = model()
            item.program_type = "internal"
            return item

Show view
=========

Show view shows one item. It is read only and doesn't allow user to change any values.

* The context of a add view is :py:class:`websauna.system.crud.CRUD.Resource` or its subclasses

Edit view
=========

Edit view updates an existing item.

Delete view
===========

Delete allows to remove one existing item.

* The base CRUD views doesn't know about the underlying model and thus cannot perform a delete. It delegates the operation to :py:attr:`websauna.system.crud.views.Delete.deleter` callback.

* The default SQLAlchemy delete callback in admin is :py:func:`websauna.system.crud.sqlalchemy.sqlalchemy_deleter`.

* Delete can be defined as *cascading* in :term:`SQLAlchemy` model. With this model set up deleting the item will delete all related items too. See :ref:`cascade`.

Resource buttons
================

One part of the CRUD view is resource buttons which allows jumping between different CRUD views.

TODO: Screenshot here

You can add these buttons yourself. Example:

.. code-block:: python

    from websauna.viewconfig import view_overrides
    from websauna.system.crud.views import TraverseLinkButton
    from websauna.system.user import adminviews as useradminviews

    from yourproject.admin import UserAdmin

    @view_overrides(context=admin.UserAdmin.Resource)
    class UserShow(useradminviews.UserShow):
        """View for displaying user information in admin."""

        # Add two more actions for the users
        resource_buttons = [

            # Default edit action
            TraverseLinkButton(id="edit", name="Edit", view_name="edit"),

            # New custom actions
            TraverseLinkButton(id="sms-user", name="Send SMS", view_name="sms-user"),
            TraverseLinkButton(id="license", name="Medical license", view_name="license")
        ]


More info
=========

See :py:mod:`websauna.system.user.adminviews` for CRUD used in the user and groups admin.