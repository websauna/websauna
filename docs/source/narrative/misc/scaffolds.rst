.. _scaffold:

=========
Scaffolds
=========

There are two different starting points for new Websauna projects. Both are available using :term:`cookiecutter` and our project templates.


Websauna Application
--------------------

To create a standalone Websauna application, use the template `cookiecutter-websauna-app`_.


Websauna Addon
--------------

To create a Python package / library which you can reuse across Websauna applications, use the template `cookiecutter-websauna-addon`_


Addon guidelines and limitations
================================

Never use :py:class:`websauna.system.model.meta.Base` but always leave models baseless and let the application plug them in with :py:func:`websauna.system.model.utils.attach_model_to_base`.

Maintain independent migration history.


Basic usage
===========

Using a Python 3 virtual environment, install cookiecutter:

    .. code-block:: console

        pip install cookiecutter


Then create a new application, following the instructions displayed by cookiecutter:

    .. code-block:: console

        cookiecutter gh:websauna/cookiecutter-websauna-app


Or a new addon:

    .. code-block:: console

        cookiecutter gh:websauna/cookiecutter-websauna-addon


.. note:: For a detailed usage guide refer to each template repository or to our tutorial.


.. _`cookiecutter-websauna-addon`: https://github.com/websauna/cookiecutter-websauna-addon
.. _`cookiecutter-websauna-app`: https://github.com/websauna/cookiecutter-websauna-app
