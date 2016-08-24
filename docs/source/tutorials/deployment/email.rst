.. _outbound-email:

==============
Outbound email
==============

.. contents:: :local:

Introduction
============

The playbook configures a local :term:`Postfix` mail service which talks to an upstream SMTP server to send out email.

* Sign up a for any transactional email service. `See this blog post by Upstream Media for a comprehensive service list <https://upshotmediagroup.com/blog/web-development/mandrill-alternatives/>`_. These services are free up to certain message amount, but usually require you to verify your domain and set up spam prevention DNS records like DKIM (DomainKeys Identity Management) and SPF (Sender Policy Framework).

* All outgoing messages are buffered locally by Postfix.

* Postfix talks to the upstream transactional email service over SMTP and sends out the messages to the world.

.. _smtp:

Configuring upstream SMTP service
=================================

In this example we sign up a `Sparkpost transaction email service <https://www.sparkpost.com/>`_.

Add Mandrill credentils to your vault:

.. code-block:: console

    ansible-vault edit secrets.yml

Add:

.. code-block:: yaml

    smtp_host: smtp.sparkpostmail.com
    smtp_port: 587
    smtp_username: SMTP_Injection
    smtp_password: 51X5G2MFJMWKOXXXXXX

Enable ``smtp`` in ``vars`` of your playbook::

  vars:
    - smtp: on

Additional variables you might want to consider when setting up email. These can be public and go to your ``playbook.yml`` directly.

.. code-block:: yaml

    # Who will receive notifications when server sends automated email
    notify_email: mikko@example.com

    # Which From: address server uses to send email
    server_email: no-reply@example.com

    # What this the suffix domain used by Postfix when generating emails from this server. Example: ``example.com``
    server_email_domain: example.com


Testing it out
==============

Run your playbook where you have enabled ``smtp: on``. For every run, it should output a test email. You can use Ansible ``smtp`` tag to run only SMTP server specific parts:

.. code-block:: console

    ansible-playbook -i hosts.ini playbook-myapp.yml -t postfix,smtp

Troubleshooting email
=====================

The usual reason for outbound email failure is due to fact that Postfix host name and domain setup does not match the whitelisted domains in the upstream transactional email service.

Log in to your server over SSH to inspect the issues. Run the troubleshooting commands as ``root``.

Below is the command line to send some mail to yourself:

.. code-block:: console

    echo "This is a test message from ${USER}@${HOSTNAME} at $(date)" \
      | sendmail mikko@example.com -f no-reply@example.com

Check the system mail queue:

.. code-block:: console

    mailq  # Should be empty

You can see Postfix logs for possible detailed error reports:

.. code-block:: console

    tail -f /var/log/mail.log

You could see something like this::

    Apr 16 21:51:20 ip-172-30-1-136 postfix/pickup[6813]: D28BE4355D: uid=0 from=<root>
    Apr 16 21:51:20 ip-172-30-1-136 postfix/cleanup[7908]: D28BE4355D: message-id=<20160416215120.D28BE4355D@app.example.com>
    Apr 16 21:51:20 ip-172-30-1-136 postfix/qmgr[6814]: D28BE4355D: from=<root@app.example.com>, size=346, nrcpt=1 (queue active)
    Apr 16 21:51:21 ip-172-30-1-136 postfix/smtp[7910]: D28BE4355D: to=<mikko@redinnovation.com>, relay=smtp.sparkpostmail.com[54.69.234.221]:587, delay=0.92, delays=0.02/0.01/0.74/0.14, dsn=5.7.1, status=bounced (host smtp.sparkpostmail.com[54.69.234.221] said: 550 5.7.1 Unconfigured Sending Domain <app.example.com> (in reply to end of DATA command))

See that Postfix answers in localhost port 25:

.. code-block:: console

    telnet localhost 25  # Write crap to the SMTP port until Postfix terminates the connection

More information
================

`Setting up SparkPost with Postfix <https://support.sparkpost.com/customer/en/portal/articles/2030960-using-sparkpost-with-postfix>`_.
