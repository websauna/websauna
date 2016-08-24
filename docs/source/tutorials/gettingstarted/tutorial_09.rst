=================
Introducing admin
=================

Websauna provides an automated :ref:`admin` interface allowing you to easily edit your modelled data through the automatically generated web interface.

Manually coding an admin site, also known as back office, for your team and clients can be tedious work that doesn’t require much creativity or contain anything novel or value adding. Websauna automates the creation of admin by automatically generating data browsers and editors for your models.

Unlike other frameworks, Websauna sites can have multiple admin interfaces. For example, one could have super admin for the developers and limited admin interfaces for customers or whitelabel owners to manage their own respective users.

Admin architecture
==================

Websauna aims to be flexible; it does not enforce any particular URL pattern one has to follow. On the contrary, the admin is based on :term:`traversal`. Any admin endpoint can declare its own hierarchy of children and grandchildren paths.

* Each model needs a corresponding admin resource of class :py:class:`websauna.system.admin.ModelAdmin`. This resource is responsible for listing and adding new items. (Actions on all items)

* Each model instance (object, a row in SQL database) needs a corresponding admin resource of class :py:class:`websauna.system.admin.ModelAdmin.Resource`. This is a nested class inside the parent ModelAdmin. This resource is responsible for show, edit and delete actions. (Actions on one item)

Including models in the admin
=============================

Models must be explicitly registered in the admin interface. For each model appearing in the admin interface a corresponding :term:`resource` class must be created in ``admins.py`` file. Resource reflects the :term:`traversal` URL part and associated :term:`views <view>`.

Edit ``admins.py`` file of ``myapp.py`` and add the following code:

.. code-block:: python

    """Admin resource registrations for your app."""

    from websauna.system.admin.modeladmin import model_admin
    from websauna.system.admin.modeladmin import ModelAdmin

    # Import our models
    from . import models


    @model_admin(traverse_id="question")
    class QuestionAdmin(ModelAdmin):
        """Admin resource for question model.

        This class declares a resource for question model admin root folder with listing and add views.
        """

        #: Label as shown in admin
        title = "Questions"

        #: Used in admin listings etc. user visible messages
        #: TODO: This mechanism will be phased out in the future versions with gettext or similar replacement for languages that have plulars one, two, many
        singular_name = "question"
        plural_name = "questions"

        #: Which models this model admin controls
        model = models.Question

        class Resource(ModelAdmin.Resource):
            """Declare resource for each individual question.

            View, edit and delete views are registered against this resource.
            """

            def get_title(self):
                """What we show as the item title in question listing."""
                return self.get_object().question_text


    @model_admin(traverse_id="choice")
    class ChoiceAdmin(ModelAdmin):
        """Admin resource for choice model."""

        title = "Choices"

        singular_name = "choice"
        plural_name = "choices"
        model = models.Choice

        class Resource(ModelAdmin.Resource):

            def get_title(self):
                return self.get_object().choice_text

Then make sure your ``__init__.py`` contain the following:

.. code-block:: python

    class Initializer:

        ...

        def configure_model_admins(self):
            """Register the models of this application."""

            # Call parent which registers user and group admins
            super(Initializer, self).configure_model_admins()

            # Scan our admins
            from . import admins
            self.config.scan(admins)

The process breakdown of adding model admins is

* Create ``admins.py`` file where you place your model admins

* Create a :py:class:`websauna.system.admin.modeladmin.ModelAdmin` subclass for each model you wish to show in admin interface

* Decorate this class with :py:class:`websauna.system.admin.modeladmin.model_admin` class decorator for configuration scan

* In ``__init__.py`` of your application, import your admin module and run ``config.scan(admin)``. The app :ref:`scaffold` should include this behavior in the default generated ``__init__.py``.

In the example, we declare two classes per each model. Here is a breakdown for *Question* model.

* ``@model_admin(traverse_id="question")`` tells that this model admin is registered under ``/admin/question`` URL.

* Class ``myapp.admins.QuestionAdmin`` is a :term:`resource` for question model admin root itself. This resource provides add question and list questions views for all questions in the database, like URL ``/admin/question/add``.

* Class ``myapp.admins.QuestionAdmin.Resource`` is a :term:`resource` for individual questions. It maps :term:`SQLAlchemy` model instance to ``/admin/question/xxxx`` URLs, so that each model instance gets its own user friendly URL path. This resource provides view question, edit question and delete question views for individual question instances, like URL ``/admin/question/xxx/edit``.

Visiting admin
==============

Start the web server or let it reload itself. Now you should see *Question* and *Choice* appear in the admin interface.

.. image:: images/question_admin.png
    :width: 640px

For example, you can edit the questions.

.. image:: images/edit_question.png
    :width: 640px

You can add new choices. For the choice you can choose the appropriate question from dropdown.

.. image:: images/add_choice.png
    :width: 640px

Further information
===================

Read :ref:`admin` documentation. Read :ref:`CRUD` documentation.

.. note ::

    TODO: Currently, it is not possible to add and edit choices from the question page. This will change in a future version.

Some examples how to customize and override views in admin interfaces

* :py:mod:`websauna.system.user.admins` module

* :py:mod:`websauna.system.user.adminviews` module

* websauna.wallet package `admins.py <https://github.com/websauna/websauna.wallet/blob/master/websauna/wallet/admins.py>`_ and `adminviews.py <https://github.com/websauna/websauna.wallet/blob/master/websauna/wallet/adminviews.py>`_


