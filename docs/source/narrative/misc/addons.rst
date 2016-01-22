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

* Addons should never inherit models from ``websauna.system.model.meta.Base`` directly, but instead of use ``websauna.system.model.meta.attach_model_to_base`` to allow the addon consumer to customize they SQLAlchemy structure

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

* Addons can hook themselves to the part of initialization process using aspect-oriented approach. :py:class:`websauna.system.Initializer` provides join points which can be hooked in with :py:func:`websauna.utils.aspect.before` and :py:func:`websauna.utils.aspect.after` decorators.

* Addon sets up its :py:class:`websauna.utils.aspect.Crosscutter` based addon initializer class and returns

* The application continues its initialization process

* Every time application hits any of initializer join points, the crosscutter gets called

Example::

    from websauna.system import Initializer
    from websauna.utils.aspect import advice_after
    from websauna.utils.aspect import Crosscutter


    class AddonInitializer(metaclass=Crosscutter):

        def __init__(self, config:Configurator):
            self.config = config

        @advice_after(Initializer.configure_templates)
        def configure_templates(self):
            """Include our package templates folder in Jinja 2 configuration."""
            self.config.add_jinja2_search_path('websauna.myaddon:templates', name='.html', prepend=False)  # HTML templates for

        def run(self):
            # Nothing here, advisors get called later
            pass


    def includeme(config: Configurator):
        init = AddonInitializer(config)
        init.run()
