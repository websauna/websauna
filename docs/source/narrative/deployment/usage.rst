=====
Usage
=====

SSH agent forwarding
====================

You need to `enable SSH agent forwarding <https://opensourcehacker.com/2012/10/24/ssh-key-and-passwordless-login-basics-for-developers/>`_, so that Ansible uses your locally configured SSH key. With this setup, the server never stores any private keys and they are safely on your own computer. Ansible uses SSH agent to make remote connections from the server to e.g. a Github to fetch source code of your application.

You can add any number of keys. The keys

* Should allow you to connect to your server (hosting provider, like Amazon EC2 key)

* Should allow you to check out source code from your repository for the deployment (Github, Bitbucket keys)

Usually the command to add a key into a SSH agent is along the lines::

    ssh-add ~/.ssh/my_ssh_private_key_for_deployment

Likewise, `you need to have set up your public key on your Git repository service like Github <https://help.github.com/articles/generating-ssh-keys/>`_.

Create playbook
===============

Example TODO:

.. code-block:: yaml


Run playbook
============

TODO

Update runs
===========

For subsequent playbook runs: If you need to only update Python files, dependencies and static assets, instead of building the server from a scratch, you can use ``site_update`` tag::

     ansible-playbook -i hosts.ini playbook-myapp.yml -t site-update

This considerably cuts down playbook execution time.

Playbook variables
==================

See :ref:`playbook variables reference <playbook-vars>` for a detailed list.
