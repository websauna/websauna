===============================
Installing Ansible and playbook
===============================

Introduction
============

:term:`Ansible` runs on your local computer and talks with the remote server over :term:`SSH`. In an ideal situation, you never need to connect to the server manually over SSH, as Ansible does all the tasks for you.

Ansible is driven by a :term:`playbook` which is effectively a linear script of commands to be run on the server. Playbooks are very human readable as is, even if you wouldn't use Ansible yourself. Playbooks are usually distributed as cloneable Git repositories.

Installation
============

Git clone the repository from Github::

    git co git@github.com:websauna/websauna.ansible.git

Create a virtual environment for Ansible. This must be separate from any other virtual environment you are working with::

    cd websauna.ansible
    virtualenv -p python2.7 venv
    source venv/bin/activate
    pip install ansible

.. note ::

    Ansible runs on Python 2.x only for now. Ansible is a Red Hat product. Red Hat is committed to support Python 2.4 for their enterprise users. As long as Python 2.4 is supported, it is impossible to upgrade Ansible to support Python 3.x due to syntax incompatibilities.

Install packaged roles we are going to use::

    ansible-galaxy install --roles-path=galaxy \
        ANXS.postgresql \
        Stouts.foundation \
        Stouts.nginx \
        Stouts.redis \
        Stouts.python


Create a vault with password. Vault is a secrets file where Ansible stores non-public configuration variables. To avoid retyping the password every time, the default password storing location is in ``~/websauna-ansible-vault.txt`` configured in ``ansible.cfg``:

.. code-block:: console

    # Read a password from keyboard and store it in a file.
    # This file is configured in ansible.cfg
    read -s pass | echo $pass > ~/websauna-ansible-vault.txt

    # Create a secrets.yml vault for your project
    ansible-vault create secrets.yml

This will open your text editor and let you edit the vault in an unencrypted format. When you quit your text editor the vault content is saved. For now you can leave it empty and just save the empty file.