=======================
Production INI settings
=======================

Websauna is mainly driven by :term:`INI` based configuration files. The most important ones are

* :ref:`production.ini` (ref:`staging.ini` for a staging deployment)

* ``production-secrets.ini`` (``staging-secrets.ini`` for a staging deployment)

``websauna.ansible`` playbook

* Generates ``production.ini`` for you

* Copies ``production-secrets.ini`` file from your local hard disk to the remote server

Example ``vars`` settings::

    # Determines if we create production.ini or staging.ini
    - site_mode: production

    # Local secrets file we copy to the server
    - ini_secrets_file: ../myapp/conf/production-secrets.ini

Customizing production.ini
==========================

Supply your own ``production.ini`` template for the playbook.
