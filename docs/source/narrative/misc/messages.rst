.. _messages:

========
Messages
========

Introduction
============

Websauna supports a message flashing. There are pop up notifications on the top of the page, usually shown to the user after the user did something and was HTTP redirected to another page.

Flash messages are stored in the user session storage which is in Redis by default.

Usage
=====

Flashing a plain text message to a logged in user:

.. code-block:: python

    from websauna.system.core import messages

    def my_view(request):

        # msg_id is passed as CSS id and is useful in functional testing
        messages.add(request, kind="info", msg="Hello world!", msg_id="msg-hello-world")


For an HTML message example please see :ref:`nag tween example <nag-tween>`.

For advanced usage see :py:func:`websauna.system.core.messages.add`.

Rendering
=========

Flash messages are rendered by :ref:`template-site/messages.html`. After rendering the flash message queue is cleared.

More information
================

See `flash messages in Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html#flash-messages>`_.