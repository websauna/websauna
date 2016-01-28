.. _mail:

=====
Email
=====

.. contents:: :local:

Introduction
============

Websauna provides facilities to send out

* `pyramid_mailer <https://github.com/Pylons/pyramid_mailer>`_ package provides low-level interface for outgoing email

* Outgoing email is tied to the success of transaction - if your code fails in some point no email is sent

* Rich-text HTML emails are supported with `premailer package <https://pypi.python.org/pypi/premailer>`_ which will turn :term:`CSS` styles to inline styles for emails


Configuring email
=================

Printing out email to console on the development server
-------------------------------------------------------

When you run a development server, no email goes out by default. Instead it is printed to your console where :ref:`ws-pserve` is running.

Sending out email
=================

Mixed HTML and plain text email
-------------------------------

Websauna supports mixed HTML + plain text emails. Websauna email messages are assembled from three different templates with a specific naming convention. Email templates are not different from web page templates, same Jinja templating engine is utilized.

* ``$message.body.html`` - HTML email body

* ``$message.body.txt`` - Plain text email body

* ``$message.subject.txt`` - Email subject

Below is a sample email.

``email/welcome.subject.txt``:

.. code-block:: jinja

    {% extends "email/base_subject.txt" %}
    {% block subject %}Welcome to {{site_name}}{% endblock %}

``email/welcome.body.txt``:

.. code-block:: jinja

    Welcome to {{ site_name }}!

    Thank you for signing up!
    Please visit the link below to see how {{ site_name }} will make your life simpler.

    {{ request.route_url('home') }}

``email/welcome.body.html``:

.. code-block:: html+jinja

    {% extends "email/base.html" %}

    {% block content %}
        <p>
        Welcome to {{site_name}},
        </p>

        <p>
        Thank you for signing up! Please visit the link below to see how {{ site_name }} will make your life simpler.
        </p>

        <p style="text-align: center">
            <a class="btn-primary" href="{{ request.route_url('home') }}">Visit {{ site_name }}</a>
        </p>

    {% endblock %}

To send this email:

.. code-block:: python

    from websauna.system.mail import send_templated_mail

    def my_view(request):
        user = request.user
        send_templated_mail(request, [user.email], "email/welcome", context={})

Raw pyramid_mail API
--------------------

Sending out test mail with raw pyramid_mailer:

    from pyramid_mailer import get_mailer
    from pyramid_mailer.message import Message

    sender = request.registry.settings["mail.default_sender"]

    message = Message(subject="pyramid_mailer test", sender="no-reply@redinnovation.com", recipients=["mikko@redinnovation.com"], body="yyy")

    mailer = get_mailer(request)
    mailer.send_immediately(message)

HTML layout
===========

To edit HTML layout and CSS styles make a copy of :ref:`email/base.html <template-email/base.html>` to your application. Edit syles inside `<style>`.

Testing HTML layout
-------------------

You can render a dummy HTML email in your browser by going to:

    http://localhost:6543/sample-html-email

See :ref:`websauna.sample_html_email` configuration for more information.