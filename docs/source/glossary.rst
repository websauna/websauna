.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   Alembic
       A migration script tool for :term:`SQLAlchemy`. `More info <http://alembic.readthedocs.org/>`_.

   development.ini
      The default configuration file when you run Websauna on your local computer when doing development. For more information see :doc:`configuration <reference/config>`.

   Initializer
      Initializer is the main entry point of your Websauna application. It is a class responsible for ramping up and integrating various subsystems. For more information see :py:class:`websauna.system.Initializer`.

   Paste
      A Python framework for building web applications on the top of `WSGI protocol <https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface>`_. See `Paste documentation <https://pypi.python.org/pypi/Paste>`_ .

   pcreate
      A command line command for creating new packages based on :term:`Pyramid` framework. `More info <http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/project.html>`_.

   pip
      A Python package installation command. `Read more <https://packaging.python.org/en/latest/installing.html>`_.

   Pyramid
      Low level web framework Python doing request routing, configuration, sessions and such. See `Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/introduction.html>`_.

   IPython
      Next generation read–eval–print loop engine for Python and other programming languages. See `IPython Notebook site <http://ipython.org/notebook.html>`_ for more information. See also :term:`IPython Notebook`.

   IPython Notebook
      A powerful browser based shell for a Python. Popular in scientific community and data analysis. See `IPython Notebook site <http://ipython.org/notebook.html>`_ for more information.

   secrets
      The secrets are passwords, API keys and other sensitive data which you want to avoid exposing.

   SQLAlchemy
      SQLAlchemy enables effortless SQL data manipulation from Python programming.

      SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. It provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language. `More information <http://www.sqlalchemy.org/>`_.

   virtual environment
      An isolated environment (folder) where all installed Python packages go. Each project should have its own virtual environment, so that different project dependencies do not mess up each other. `Read more <https://packaging.python.org/en/latest/installing.html>`_.