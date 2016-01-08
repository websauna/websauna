========
Messages
========

Introduction
============

Websauna supports a message flashing. There are pop up notifications on the top of the page, usually shown to the user after the user did something and was HTTP redirected to another page.

Flash messages are stored in the user session storage which is in Redis by default.

Usage
=====

See :py:mod:`websauna.system.core.messages`.

Rendering
=========

Flash messages are rendered by ``site/messages.html``. After rendering the flash message queue is cleared.

More information
================

See `flash messages in Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html#flash-messages>`_.