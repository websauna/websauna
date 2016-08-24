================================
Creating web application project
================================

Websauna comes with two project scaffolds ``websauna_app`` and ``websauna_addon``. We create the first application here.

Creating application package
============================

Enter to your project folder and make sure the :term:`virtual environment` is active on your shell::

    cd myproject
    source venv/bin/activate

Websauna uses :term:`Pyramid`'s :term:`pcreate` command and a scaffold mechanism to bootstrap a new project. The `pcreate` command is installed in `venv/bin` folder. To create your application, type::

    pcreate -t websauna_app myapp  # Replace myapp with a creative all lowercase alphanumeric name

This will create a project structure similar to::

    myapp/                          # Python package root
    myapp/myapp                     # Python module "myapp" with all .py files
    myapp/myapp/__init__.py         # Application entry point with Websauna Initializer
    myapp/myapp/static              # Images, CSS and JavaScript
    myapp/myapp/templates           # Jinja2 page templates
    myapp/myapp/tests               # Automatic test suite
    myapp/alembic                   # Database migration scripts
    myapp/conf                      # Config files
    myapp/setup.py                  # Python package data

Installing application package
==============================

After you have created your application, you need to install it to your current :term:`virtual environment`.

Install the package in edit mode, including Python package dependencies needed for testing, using :term:`pip`::

    pip install -e "myapp[test]"
