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

Clone the repository from GitHub to get started with your Playbook:

.. code-block:: console

    git clone git@github.com:websauna/websauna.ansible.git

Create a :term:`virtual environment` for Ansible. This must be a separate from the virtual environment of your application due to Python version differences:

.. code-block:: console

    cd websauna.ansible
    virtualenv -p python2.7 venv
    source venv/bin/activate

And install Ansible using pip.
On Linux:

.. code-block:: console
   
   pip install "ansible<2.2"  # Stouts.nginx is currently incompatible with latest Ansible

On macOS (recent macOS versions do not ship with OpenSSL, so instead of above `pip` command do):

.. code-block:: console

    brew install openssl --force
    echo 'export PATH="/usr/local/opt/openssl/bin:$PATH"' >> ~/.zshrc # zsh
    env LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include" CFLAGS="-I/usr/local/opt/openssl/include" pip install "ansible<2.2"

.. note::

    Ansible runs on Python 2.x only. Ansible is a Red Hat product. Red Hat is committed to support Python 2.4 for their enterprise users. As long as Python 2.4 is supported, it is impossible to upgrade Ansible to support Python 3.x due to syntax incompatibilities.

Install packaged roles we are going to use inside a cloned playbook. They will be dropped in ``galaxy`` folder inside the playbook folder:

.. code-block:: console

    ansible-galaxy install -r requirements.yml

Creating Ansible vault
======================

Create an Ansible :term:`vault` with a password. The vault is a secrets file where Ansible stores non-public configuration variables. To avoid retyping the password every time, the password is saved in plaintext in your home folder or any other safe location. The default password storing location is in ``~/websauna-ansible-vault.txt`` as configured in ``ansible.cfg``:

.. code-block:: console

    # Read a password from keyboard and store it in a file.
    # This file is configured in ansible.cfg
    read -s pass | echo $pass > ~/websauna-ansible-vault.txt

    # Create a secrets.yml vault for your project
    ansible-vault create secrets.yml

This will open your text editor and let you edit the vault in an unencrypted format.

* You do not need to add anything in this file for now. It will be filled in later in the instructions.

* Save file

* Quit your text editor to get back to the command line

Using alternative text editor with Ansible vault
------------------------------------------------

You can specify any command line compatible editor for vault editing. For example on OSX one could do:

.. code-block:: console

    # Use default OSX text edit as vault editor
    export EDITOR="/usr/bin/open -n -W -a /Applications/TextEdit.app"

    # Create a secrets.yml vault for your project using TextEdit
    ansible-vault create secrets.yml

`More information using UNIX EDITOR environment variable (Ubuntu) <http://askubuntu.com/questions/432524/how-do-i-find-and-set-my-editor-environment-variable>`_.

`More information using UNIX EDITOR environment variable (OSX) <http://stackoverflow.com/questions/3539594/change-the-default-editor-for-files-opened-in-the-terminal-e-g-set-it-to-text>`_.
