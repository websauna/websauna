================================
Creating web application project
================================

Websauna community maintains two :term:`cookiecutter` project templates: ``cookiecutter-websauna-app`` and ``cookiecutter-websauna-addon``. We create the first application here.


Creating application package
============================

Enter to your project folder and make sure the :term:`virtual environment` is active on your shell:

    .. code-block:: console
        
        cd myproject
        source venv/bin/activate


Websauna uses :term:`cookiecutter` tool to bootstrap a new project. To install it, inside this :term:`virtual environment`, type:

    .. code-block:: console

        pip install cookiecutter


Now, it is possible to create a new application:

    .. code-block:: console
    
        cookiecutter gh:websauna/cookiecutter-websauna-app


**Warning**: After this point, change 'Amazing Team', 'websauna', etc to your own information.

Answer the prompts with your own desired options. For example:

    .. code-block:: console

        full_name [Amazing Team]: Amazing Team
        email [team@mycompany.com]: team@company.com
        company [Websauna]: Company
        github_username [websauna]: company
        project_name [My Package]: My Application
        project_short_description [A nice and short description.]: Another Websauna application
        tags [python package websauna pyramid]: python package websauna pyramid
        repo_name [websauna.package]: company.application
        namespace [company]: company
        package_name [application]: application
        release_date [today]:
        year [2017]:
        version [1.0.0a1]:
        authentication_random [82e7affc6b55e58dd962e74e37dedc19679c92b9]:
        authomatic_random [22539423a5ceb1fe6f7c6cd1a3a1867315236f25]:
        session_random [1261a92aa68dc52877d8d2606943a4fb69ca0879]:


.. note:: We recommend you accept the values presented for authentication_random, authomatic_random, session_random
          as they were generated for this execution.


After a while, the generation will be finished and the following message will be displayed:

    .. code-block:: console

        ===============================================================================
        Websauna Application.
        Package company.application was generated.
        Now, code it, create a git repository, push to your GitHub account.
        Sorry for the convenience.
        ===============================================================================


This will create a project structure similar to::

    company.application/                                        # Python package root
    company.application/alembic                                 # Database migration scripts
    company.application/company                                 # Python namespace "company" with all .py files
    company.application/company/application                     # Python module "application" with all .py files
    company.application/company/application/__init__.py         # Application entry point with Websauna Initializer
    company.application/company/application/conf                # Config files
    company.application/company/application/static              # Images, CSS and JavaScript
    company.application/company/application/templates           # Jinja2 page templates
    company.application/company/application/tests               # Automatic test suite
    company.application/setup.py                                # Python package data


Installing application package
==============================

After you have created your application, you need to install it to your current :term:`virtual environment`.

Install the package in edit mode, including Python package dependencies needed for development and testing, using :term:`pip`:

    .. code-block:: console

        pip install -e ".[dev,test]"

