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

Use ``pcreate`` command with ``websauna_addon`` scaffold.


Example addons
--------------

TODO