.. _glossary:

Glossary
========

.. glossary::
    :sorted:

    ACID
        In computer science, ACID (Atomicity, Consistency, Isolation, Durability) is a set of properties that guarantee that database transactions are processed reliably. `More info <https://en.wikipedia.org/wiki/ACID>`__.

    Alembic
       A migration script tool for :term:`SQLAlchemy`. `More info <http://alembic.readthedocs.org/>`__.

    development.ini
      The default configuration file when you run Websauna on your local computer when doing development. For more information see :doc:`configuration <reference/config>`.

    Celery
      Celery a task queue for Python with focus on real-time processing, while also supporting task scheduling. `More info <http://celery.readthedocs.org/>`__.

    duplicity
        Duplicity backs directories by producing encrypted tar-format volumes and uploading them to a remote or local file server. Because duplicity uses librsync, the incremental archives are space efficient and only record the parts of files that have changed since the last backup. Because duplicity uses GnuPG to encrypt and/or sign these archives, they will be safe from spying and/or modification by the server. `More info <http://duplicity.nongnu.org/>`__.

    git
      The most popular version control software at the moment. `More info <https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control>`__.

    .gitignore
      A mechanism to avoid placing files under a git version control by blacklisting them.

    Initializer
        Initializer is the main entry point of your Websauna application. It is a class responsible for ramping up and integrating various subsystems. For more information see :py:class:`websauna.system.Initializer`.

    JSON
        JSON, JavaScript Object Notation, specified by RFC 7159 and by ECMA-404, is a lightweight data interchange format inspired by JavaScript object literal syntax. Most web related programming languages and support JSON as an exchange format. `Read more <https://en.wikipedia.org/wiki/Json/>`__.

    JSONB
        A :term:`PostgreSQL` column type to store JSON structured data. `Read more <https://www.compose.io/articles/is-postgresql-your-next-json-database/>`__.

    Paste
      A Python framework for building web applications on the top of `WSGI protocol <https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface>`__. See `Paste documentation <https://pypi.python.org/pypi/Paste>`__ .

    pcreate
      A command line command for creating new packages based on :term:`Pyramid` framework. `More info <http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/project.html>`__.

    pip
      A Python package installation command. `Read more <https://packaging.python.org/en/latest/installing.html>`__.

    Pyramid
        Low level web framework Python doing request routing, configuration, sessions and such. See `Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/introduction.html>`__.

    pyramid_celery
        A Celery integration for Pyramid. `More info <https://github.com/sontek/pyramid_celery>`__.

    pyramid_debugtoolbar
        A package to collect and show various debug and diagnose information from a local Pyramid development server. `More info <http://docs.pylonsproject.org/projects/pyramid-debugtoolbar/en/latest/>`__.

    IPython
        Next generation read–eval–print loop engine for Python and other programming languages. See `IPython Notebook site <http://ipython.org/notebook.html>`__ for more information. See also :term:`IPython Notebook`.

    IPython Notebook
        A powerful browser based shell for a Python. Popular in scientific community and data analysis. See `IPython Notebook site <http://ipython.org/notebook.html>`__ for more information.

    PostgreSQL
        The world's most advanced open source database. PostgreSQL is a powerful, open source object-relational database system. It has more than 15 years of active development and a proven architecture that has earned it a strong reputation for reliability, data integrity, and correctness. `More information <http://postgresql.org/>`__.

    Redis
        Redis is an open source (BSD licensed), in-memory data structure store, used as database, cache and message broker. It supports data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs and geospatial indexes with radius queries. `More information <http://redis.io/>`__.

    scaffold
        A project skeleton which generates a starting point for your application. Websauna uses `Pyramid scaffolding <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/scaffolding.html>`__ for its ``websauna_app`` and ``websauna_addon`` scaffols.

    secrets
        The secrets are passwords, API keys and other sensitive data which you want to avoid exposing.

    SQLAlchemy
        SQLAlchemy enables effortless SQL data manipulation from Python programming.

        SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. It provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language. `More information <http://www.sqlalchemy.org/>`__.

    virtual environment
        An isolated environment (folder) where all installed Python packages go. Each project should have its own virtual environment, so that different project dependencies do not mess up each other. `Read more <https://packaging.python.org/en/latest/installing.html>`__.