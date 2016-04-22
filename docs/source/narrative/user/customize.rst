=========================
Customizing user behavior
=========================

.. contents:: :local:

Introduction
============

Websauna allows you to override user subsystem parts on multiple levels

* Form fields and validation a.k.a. schemas (see :ref:`forms`, see :py:meth:`websauna.system.Initializer.configure_user_forms`)

* Form objects (see :ref:`forms`, see :py:meth:`websauna.system.Initializer.configure_user_forms`)

* Templates (see :ref:`templates`, see :py:meth:`websauna.system.Initializer.configure_user`)

* Views (see :ref:`views`, see :py:meth:`websauna.system.Initializer.configure_user`)

* Services (see :ref:`User log in and sign up user-services <user-services>`)

* :ref:`SQLAlchemy models <models>` for user database in the database (see :py:meth:`websauna.system.Initializer.configure_user_models`)

.. _customize-user-form:

Customizing user forms
======================

User related forms and fields are set up in :py:meth:`websauna.system.Initializer.configure_user_forms`.

Below is an example how to override a sign in form button.

Create ``forms.py``:

.. code-block:: python

    from deform import Form
    from deform import  Button

    class CustomLoginForm(Form):

        def __init__(self, *args, **kwargs):
            login_button = Button(name="login_email", title="Login by fingerprint", css_class="btn-lg btn-block")
            kwargs['buttons'] = (login_button,)
            super().__init__(*args, **kwargs)

Then you can use this form instead of the default one by overriding :py:meth:`websauna.system.Initializer.configure_user_forms` in your app initializer.

``__init__.py``:

.. code-block:: python

        from websauna.system.user.interfaces import ILoginForm
        from .forms import CustomLoginForm


        class Initializer(websauna.system.Initializer):

            def configure_user_forms(self):

                # This will set up all default forms as shown in websauna.system.Initializer.configure_user_forms
                super(Initializer, self).configure_user_forms()

                # Override the default login form with custom one
                self.config.registry.unregisterUtility(provided=ILoginForm)
                self.config.registry.registerUtility(CustomLoginForm, ILoginForm)