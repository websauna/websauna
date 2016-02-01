===============================
Installing Ansible and playbook
===============================

Introduction
============

:term:`Ansible` runs on your local computer and talks with the remote server over :term:`SSH`. In an ideal situation, you never need to connect to the server manually over SSH, as Ansible does all the tasks for you.

Ansible is driven by a :term:`playbook` which is effectively a linear script of commands to be run on the server. Playbooks are very human readable as is, even if you wouldn't use Ansible yourself. Playbooks are usually distributed as cloneable Git repositories.

Installation
============

Websauna's playbook ``websauna.ansible`` is provided in a separate :term:`Git` repository. See `websauna.ansible Git repository <https://github.com/websauna/websauna.ansible>`_.

Clone the repository from Github to get started with your Playbook:

.. code-block:: console

    git co git@github.com:websauna/websauna.ansible.git

Create a :term:`virtual environment` for Ansible. This must be a separate from the virtual environment of your application due to Python version differences:

.. code-block:: console

    cd websauna.ansible
    virtualenv -p python2.7 venv
    source venv/bin/activate
    pip install ansible

.. note ::

    Ansible runs on Python 2.x only. Ansible is a Red Hat product. Red Hat is committed to support Python 2.4 for their enterprise users. As long as Python 2.4 is supported, it is impossible to upgrade Ansible to support Python 3.x due to syntax incompatibilities.

Install packaged roles we are going to use inside a cloned playbook. They will be dropped in ``galaxy`` folder inside the playbook folder:

.. code-block:: console

    ansible-galaxy install --roles-path=galaxy \
        ANXS.postgresql \
        ANXS.logwatch \
        Stouts.foundation \
        Stouts.nginx \
        Stouts.redis \
        Stouts.python


Create an Ansible :term:`vault` with a password. The vault is a secrets file where Ansible stores non-public configuration variables. To avoid retyping the password every time, the password is saved in plaintext in your home folder or any other safe location. The default password storing location is in ``~/websauna-ansible-vault.txt`` as configured in ``ansible.cfg``:

.. code-block:: console

    # Read a password from keyboard and store it in a file.
    # This file is configured in ansible.cfg
    read -s pass | echo $pass > ~/websauna-ansible-vault.txt

    # Create a secrets.yml vault for your project
    ansible-vault create secrets.yml

This will open your text editor and let you edit the vault in an unencrypted format. When you quit your text editor the vault content is saved. For now you can leave it empty and just save the empty file.