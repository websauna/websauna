Troubleshooting
===============

Manually SSH'ing in the box and checking why website doesn't start up
---------------------------------------------------------------------

SSH in to your server. If you are using Vagrant local testing you can do::

    vagrant ssh

Change to ``wsgi`` user::

    sudo -i -u wsgi

It should go directly the deployment folder, virtual environment activated::

    (venv)wsgi@vagrant-ubuntu-trusty-64:/srv/pyramid/myapp$

Test shell::

    ws-shell conf/production.ini

This will usually show import errors.

Test local web server::

    ws-pserve conf/production.ini

This will usually show if your database is not in migrated state or PostgreSQL or Redis is not running properly.

Ansible variable ordering
-------------------------

See

* https://github.com/edx/configuration/wiki/Ansible-variable-conventions-and-overriding-defaults
