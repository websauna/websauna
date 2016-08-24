============
Staging site
============

Introduction
============

Staging site is a non-public copy of the production site for testing rollouts before a release.

Password protection
===================

Staging site may run in a public IP address, but must never be public.

Websauna playbook protects the staging site with a :term:`htpasswd` password on Nginx level. This password is stored in Ansible :term:`vault`.

To set up a password to access the staging site, open vault:

.. code-block:: console

    ansible-vault edit secrets.yml

Add two new varibles::

    htpasswd_user: super
    htpasswd_password: secret

In your playbook file make sure staging behavior is turned on:

.. code-block:: yaml

    vars:
    # ...
    - site_mode: staging
