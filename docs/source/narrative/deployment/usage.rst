=====
Usage
=====

SSH agent forwarding
--------------------

You need to `enable SSH agent forwarding <https://opensourcehacker.com/2012/10/24/ssh-key-and-passwordless-login-basics-for-developers/>`_, so that Ansible uses your locally configured SSH key.

Usually the command is along the lines::

    ssh-add ~/.ssh/my_ssh_private_key_for_deployment

Likewise, `you need to have set up your public key on your Git repository service like Github <https://help.github.com/articles/generating-ssh-keys/>`_.

Run playbook
============

TODO

Update runs
===========

For subsequent playbook runs: If you need to only update Python files, dependencies and static assets, instead of building the server from a scratch, you can use ``site_update`` tag::

     ansible-playbook -i hosts.ini playbook-myapp.yml -t site-update

This considerably cuts down playbook execution time.


