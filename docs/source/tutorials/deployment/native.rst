===================
Native dependencies
===================

.. contents:: :local:

Introduction
============

Native dependencies refer here to Linux system packages in order to make your web application install or run. Native dependencies usually are C libraries that are prerequsites for installing Python packages.

Including native dependencies
=============================

Edit your ``playbook.yml`` file and add an ``apt`` section in ``pre_tasks``:

.. code-block:: yaml

  pre_tasks:

    # Load default vars based on playbook.yml input
    - include_vars: default.yml
      tags: site, smtp

    # Load default vars based on playbook.yml input
    - include_vars: secrets.yml
      tags: site, smtp

    # Installs smartcard libraries needed for Python DESFire packages
    - name: Install project native dependencies
      apt: pkg={{ item }} update_cache=no cache_valid_time=86400
      with_items:
         - libffi-dev
         - libsqlite3-dev
         - swig
         - swig3.0
         - libpcsclite-dev
         - pcscd
      become: yes
      become_user: root
      tags: site
