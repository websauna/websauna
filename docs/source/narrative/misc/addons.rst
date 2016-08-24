========================
Creating Websauna addons
========================

Websauna supports reusable addon packages which bring additional functionality to your application. The functionality may include

* Additional forms and widgets

* Additional functionality, like SMS messaging and two-factor authentication

* Different user models and backends

Addons vs. applications
-----------------------

* Addons live in websauna namespace. E.g. an addon package could be ``websauna.yourpackage``.

* Addon must be initialized by calling ``config.include(`websauna.youraddon`)`` Pyramid inclusion mechanism in the application :term:`initializer`

* Addons have their own Alembic migration table

* Addons should never inherit models from ``websauna.system.model.meta.Base`` directly, but instead use ``websauna.system.model.meta.attach_model_to_base`` to allow the addon consumer to customize they SQLAlchemy structure

Creating addon
--------------

* Use ``pcreate`` command with ``websauna_addon`` scaffold.

* Install addon to your virtualenv after creation: ``pip install -e .["test"]``

Example addons
--------------

TODO

Addon initialization process
----------------------------

* Websauna application initializer calls ``includeme()`` entry points very early in the application initialization process, right after :py:class:`pyramid.config.Configurator` and logging have been set up

* Addons can hook themselves to the part of initialization process using events. :py:class:`websauna.system.Initializer` provides join points which can be hooked in with :py:func:`websauna.utils.autoevent.before` and :py:func:`websauna.utils.autoevent.after` decorators.

* Addon sets up its addon initializer instance and bind it to application initializer using :py:func:`websauna.utils.autoevent.bind_events`.

* The application continues its initialization process

* Every time application hits any of event source methods, the addon event hooks get called

Example::

    from websauna.system import Initializer
    from websauna.utils.autoevent import after
    from websauna.utils.autoevent import bind_events


    class AddonInitializer:

        def __init__(self, config:Configurator):
            self.config = config

        @after(Initializer.configure_templates)
        def configure_templates(self):
            """Include our package templates folder in Jinja 2 configuration."""
            self.config.add_jinja2_search_path('websauna.myaddon:templates', name='.html', prepend=False)  # HTML templates for

        def run(self):
            # Nothing here, advisors get called later
            bind_event(self.config.registry.initializer, self)


    def includeme(config: Configurator):
        init = AddonInitializer(config)
        init.run()

Creating addon migrations
-------------------------

When you manipulate addon models and add new fields you need to create migrations specific to addon.

Easiest way to do this is to develop against addon :ref:`development.ini` and use addon specific development database.

TODO
