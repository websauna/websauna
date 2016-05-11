======
Tweens
======

.. contents:: :local:

Introduction
============

Tweens is a middleware subsystem for Pyramid framework. It allows you to run code before and after processing HTTP request. `See main Pyramid article <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#registering-tweens>`_.

.. _nag-tween:

Creating a tween
================

The following tween keeps nagging the user every time a page is loaded if the user profile information is incomplete.

``tweens.py``:

.. code-block:: python

    from pyramid.registry import Registry
    from pyramid.renderers import render

    from websauna.system.http import Request
    from websauna.system.core import messages


    class NagTween:
        """Remind user on every page load that the user profile info is incomplete.
        """

        def __init__(self, handler, registry: Registry):
            self.handler = handler
            self.registry = registry

        def nag(self, request):
            html = render("views/profile_nag.html", {}, request=request)
            messages.add(request, kind="info", msg=html, html=True)

        def __call__(self, request: Request):
            user = request.user
            if user:
                if not user.full_name:
                    self.nag(request)

            response = self.handler(request)
            return response

``profile_nag.html``:

.. code-block:: html+jinja

    Please complete your <a href="{{ 'profile'| route_url }}"><strong>user profile information</strong></a>.

Registering a tween
===================

In your :py:meth:`websauna.system.Initializer.configure_tweens`:

.. code-block:: python

    pyramid.tweens

    # ...

    def configure_tweens(self):
        super()
        self.config.add_tween("exampleapp.tweens.NagTween", over=pyramid.tweens.MAIN)


Default tweens
==============

See

* :py:class:`websauna.system.auth.tweens.SessionInvalidationTweenFactory`

Displaying tween stack
======================

Please see :ref:`ws-tweens` command.



