.. _crud-url-mapping:

===========
URL mapping
===========

.. contents:: :local:

Introduction
============

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