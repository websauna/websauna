.. _settings:

========
Settings
========

.. contents:: :local:

Introduction
============

:term:`Pyramid` framework provides basic configuration file support for applications. It is :term:`INI` file based. Websauna provides its own inclusion mechanism over settings files.

* Websauna core settings are documented :ref:`here <config>`

* Websauna addons and Pyramid packages can have their own settings in the configuration files

* Your application can have its own settings. For example, you might want to switch between API service endpoints for ``development.ini``, ``production.ini`` and ``test.ini``

Accessing settings
==================

Pyramid :py:class:`pyramid.registry.Registry` exposes settings as dictionary ``registry.settings``.

Accessing settings in views
---------------------------

Registry is exposed vie ``request.registry``. Example:

.. code-block:: python

Example:

.. code-block:: python

    from pyramid.settings import aslist


    def my_view(request):

        settings = request.registry.settings
        # Get a list of enabled social logins
        social_logins = aslist(settings.get("websauna.social_logins", ""))


Accessing settings in initialization
------------------------------------

For :py:class:`websauna.system.Initializer` you can use ``self.settings`` (also available through ``self.config.registry.settings`` via :py:class:`pyramid.config.Configurator`.

Example:

.. code-block:: python

    from pyramid.settings import asbool

    class Initializer:

        # ...

        def make_wsgi_app(self, sanity_check=True):

            # Get boolean settings
            sanity_check = asbool(self.settings.get("websauna.sanity_check", True))

            # Now use it
            if sanity_check:
                self.perform_sanity_check()


More information
----------------

See also

* :py:func:`pyramid.settings.asbool` - parse boolean value from raw string setting

* :py:func:`pyramid.settings.aslist` - parse list of values from raw string setting


Settings file inclusion mechanism
=================================

See :ref:`configuration structure <configuration-structure>`.

Choosing settings in testing
============================

See :ref:`test.ini` instructions.

Future compatibility
====================

Long term plan is to replace INI files with more robust and extensible solution.
