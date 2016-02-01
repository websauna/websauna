==============
Outgoing email
==============

Introduction
============

Playbook configures a local :term:`Postfix` mail server on the server. For the convenience, it is recommended to use free :term:`Mandrill` account as upstream SMTP server.

.. _mandrill:

Setting up email
================

Sign up to `mandrill.com <https://mandrill.com>`_. You get up to 12 000 monthly emails for free for reputable SMTP servers.

Add Mandrill credentils to your vault::

    ansible-vault edit secrets.yml

Add::

    # your Mandrill sign in email is your Mandrill username
    mandrill_username: mikko@example.com
    mandrill_api_key: 51X5G2MFJMWKOXXXXXX

Enable ``mandrill`` in ``vars`` of your playbook::

  vars:
    - mandrill: on


`More information about Postfix and Mandrill <http://opensourcehacker.com/2013/03/26/using-postfix-and-free-mandrill-email-service-for-smtp-on-ubuntu-linux-server/>`_.