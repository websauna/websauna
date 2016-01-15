=================
Introducing admin
=================

Websauna provides automated :doc:`admin interface <../../narrative/modelling/admin>` for managing your data.

Generating admin sites for your staff or clients to add, change, and delete content is tedious work that doesn’t require much creativity. For that reason, Websauna mostly automates creation of admin interfaces for models.

.. note ::

    Unlike many similiar frameworks, Websauna can have multiple admin interfaces at once. For example, one super admin for the developers and another admins for whitelabel owners to manage their subsites and customers.

Admin architecture
==================

Websauna aims to be flexible; it does not enforce any particular URL pattern on the interface. On the contrary, the admin is based on :term:`traversal`. Any admin endpoint can declare its own hierarchy of children and grandchildren paths.

* Each model needs a corresponding admin resource of class :py:class:`websauna.system.admin.ModelAdmin`. This resource is responsible for listing and adding new items. (Actions on all items)

* Each model instance (object, a row in SQL database) needs a corresponding admin resource of class :py:class:`websauna.system.admin.ModelAdmin.Resource`. This is a nested class inside the parent ModelAdmin. This resource is responsible for show, edit and delete actions. (Actions on one item)

Including models in the admin
=============================

For each model appearing in the admin interface a corresponding :term:`resource` class must be created in ``admins.py`` file.


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

.. note ::

    TODO: Currently there is not possibility to add and edit question choices inline from the question page. This will change in the future versions.

