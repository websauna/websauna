=====
Email
=====

Introduction
============

Websauna provides facilities to send out

* `pyramid_mailer <https://github.com/Pylons/pyramid_mailer>`_ package provides low-level interface for outgoing email

* Outgoing email is tied to the success of transaction - if your code fails in some point no email is sent

* Rich-text HTML emails are supported with `premailer package <https://pypi.python.org/pypi/premailer>`_

Configuring email
=================

Printing out email to console on the development server
-------------------------------------------------------

Sending out email
-----------------

Sending out test mail:

    from pyramid_mailer import get_mailer
    from pyramid_mailer.message import Message

    sender = request.registry.settings["mail.default_sender"]

    message = Message(subject="pyramid_mailer test", sender="no-reply@redinnovation.com", recipients=["mikko@redinnovation.com"], body="yyy")

    mailer = get_mailer(request)
    mailer.send_immediately(message)

