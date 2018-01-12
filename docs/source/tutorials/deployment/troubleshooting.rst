Troubleshooting
===============

.. contents:: :local:

Ansible hangs at Install Python packages (pip) task
---------------------------------------------------

Ansible ``pip`` module is buggy and `does not correctly abort when pip asks for interactive user interaction <https://github.com/ansible/ansible-modules-core/issues/2697>`_.

The workaround is to manually log in to the server and run pip, see where it hangs and answer the question.

Example:

.. code-block:: console

    ssh -A yourserver  # Login to the server, SSH agent enabled
    sudo -i -u wsgi  # Switch to wsgi user under which your web application runs
    cd /srv/pyramid/yourapp  # Go to the folder where your application git checkout is
    source venv/bin/activate  # Activate virtual environment where your application Python packages are installed
    pip install -r requirements.txt  # Run pip and now it runs interactively in your terminal



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

    ws-pserve ws://conf/production.ini

This will usually show if your database is not in migrated state or PostgreSQL or Redis is not running properly.

Ansible variable ordering
-------------------------

See

* https://github.com/edx/configuration/wiki/Ansible-variable-conventions-and-overriding-defaults
