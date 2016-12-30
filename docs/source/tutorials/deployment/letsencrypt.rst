====================================
Let's Encrypt certificates for HTTPS
====================================

.. contents:: :local:

Introduction
============

`Let's Encrypt <https://letsencrypt.org/>`_ is a non-profit service provising free TLS (HTTPS) certificates with automated installation process. This chapter shows how to integrate Let's Encrypt for HTTPS certificates with *websauna.ansible* playbook and Nginx.

These instructions will set up a cron job that automatically updates Lets Encrypt certificates before their 3 months expiration time is up.

Installation
============

You need ``ansible-letsencrypt`` role that is known to be compatible with Websauna playbook. In the folder where you have ``playbook.yml`` file create or append  ``requirements.yml`` with the contents:

.. code-block:: yaml

    - src: git+https://github.com/websauna/ansible-letsencrypt.git
      name: ansible-letsencrypt

Then install the requirement:

.. code-block:: console

    ansible-galaxy install -r requirements.yml

Setting up a playbook
=====================

Here are the main settings you need to change. `See fully functional playbook example <https://github.com/websauna/websauna.ansible/blob/master/playbook-letsencrypt.yml>`_.

Important variables:

.. code-block:: yaml

    - letsencrypt: on
    - ssl: on

    # Let's encrypt parameters
    - server_name: letsencrypt.websauna.org  # Your server fully qualified domain name
    - letsencrypt_webroot_path: /var/www/html
    - letsencrypt_email: mikko@opensourcehacker.net  # Your email
    - letsencrypt_cert_domains:
      - "{{ server_name }}"
    - letsencrypt_renewal_command_args: '--renew-hook "service nginx restart"'  # Ubuntu 14.04 nginx restart
    - nginx_ssl_certificate_path: "/etc/letsencrypt/live/{{ server_name }}/cert.pem"
    - nginx_ssl_certificate_path_key: "/etc/letsencrypt/live/{{ server_name }}/privkey.pem"

New role ``letsencrypt`` as:

.. code-block:: yaml

    roles:
      # ...
      - { role: Stouts.python, become: yes, become_user: root }
      - {role: ansible-letsencrypt, tags: 'letsencrypt'}
      - { role: websauna.site, tags: ['site'] }  # Core site update logic
      # ...

Rerun full playbook to make changes effective.

More information
================

`Known Good Let's Encrypt role for Ansible <https://github.com/websauna/ansible-letsencrypt>`_.

`See fully functional playbook example <https://github.com/websauna/websauna.ansible/blob/master/playbook-letsencrypt.yml>`_.
