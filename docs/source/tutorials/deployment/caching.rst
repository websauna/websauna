============================
Disabling production caching
============================

.. contents:: :local:

Introduction
============

Sometimes it is useful to make your deployed server run in a development-like mode, so that CSS, JS and template files are reloaded on every refresh. This allows e.g. website designers to access and edit the site templates without need to have complex toolchain in place to run the site locally.

This page contains some instructions how to make your playbook to deploy a site in reload friendly manner.

Unset cache time
================

Make sure you are not sending *Expires* HTTP headers.

Add:

.. code-block:: yaml

    - ini_extra_settings: |
        websauna.cache_max_age_seconds  = 0

To ``vars`` section in your playbook.




