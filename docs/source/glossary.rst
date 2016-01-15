.. _glossary:

Glossary
========

.. glossary::
    :sorted:

    ACID
        In computer science, ACID (Atomicity, Consistency, Isolation, Durability) is a set of properties that guarantee that database transactions are processed reliably. `More info <https://en.wikipedia.org/wiki/ACID>`__.

    Alembic
       A migration script tool for :term:`SQLAlchemy`. `More info <http://alembic.readthedocs.org/>`__.

    Bootstrap
        Bootstrap is the most popular HTML, CSS, and JS framework for developing responsive, mobile first projects on the web. `More informatin <http://getbootstrap.com/>`__.

    database
        A database is an organized collection of data. A database management system (DBMS) is a computer software application that interacts with the user, other applications, and the database itself to capture and analyze data. A general-purpose DBMS is designed to allow the definition, creation, querying, update, and administration of databases. Websauna defaults to :term:`PostgreSQL` DBMS.

    development.ini
      The default configuration file when you run Websauna on your local computer when doing development. For more information see :doc:`configuration <reference/config>`.

    Celery
      Celery a task queue for Python with focus on real-time processing, while also supporting task scheduling. `More info <http://celery.readthedocs.org/>`__.

    CRUD
        In computer programming, create, read, update and delete, sometimes called SCRUD with an "S" for Search, are the four basic functions of persistent storage. :doc:`Read about CRUD in Websauna <../narrative/modelling/crud>`.
        `More info <https://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`__.

    CSRF
        Cross-site request forgery, also known as one-click attack or session riding and abbreviated as CSRF (sometimes pronounced sea-surf) or XSRF, is a type of malicious exploit of a website where unauthorized commands are transmitted from a user that the website trusts. `More info <https://en.wikipedia.org/wiki/Cross-site_request_forgery>`__.

    CSS
        Cascading Style Sheets (CSS) is a style sheet language used for describing the presentation of a document written in a markup language. It's most often used to set the visual style of web pages and user interfaces written in HTML and XHTML. `More info <https://en.wikipedia.org/wiki/Cascading_Style_Sheets>`__.

    development
        Development is the stage of the deployment when the developer is locally working on the code on a local machine. See :ref:`development.ini`.

    duplicity
        Duplicity backs directories by producing encrypted tar-format volumes and uploading them to a remote or local file server. Because duplicity uses librsync, the incremental archives are space efficient and only record the parts of files that have changed since the last backup. Because duplicity uses GnuPG to encrypt and/or sign these archives, they will be safe from spying and/or modification by the server. `More info <http://duplicity.nongnu.org/>`__.

    git
      The most popular version control software at the moment. `More info <https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control>`__.

    .gitignore
      A mechanism to avoid placing files under a git version control by blacklisting them.

    Initializer
        Initializer is the main entry point of your Websauna application. It is a class responsible for ramping up and integrating various subsystems. For more information see :py:class:`websauna.system.Initializer`.

    Jinja
        Jinja2 is a modern and designer-friendly templating language for Python, modelled after Django’s templates. It is fast, widely used and secure with the optional sandboxed template execution environment. `Read more <http://jinja.pocoo.org/docs/dev//>`__.

    JSON
        JSON, JavaScript Object Notation, specified by RFC 7159 and by ECMA-404, is a lightweight data interchange format inspired by JavaScript object literal syntax. Most web related programming languages and support JSON as an exchange format. `Read more <https://en.wikipedia.org/wiki/Json/>`__.

    JSONB
        A :term:`PostgreSQL` column type to store JSON structured data. `Read more <https://www.compose.io/articles/is-postgresql-your-next-json-database/>`__.

    model
        A model is a Python class describing :term:`persistent` data structure. A model provides convenient Python API to manipulate your data, so that save and load it into a :term:`database`. :doc:`More information <../narrative/modelling/models>`.

    migration
        Data migration refers to procedure of changing how data is stored in your database - adding new data columns or changing how old columns behave. It is usually performed one time batch operation per database. Read :doc:`Websauna migrations documentation <../narrative/ops/migrations>`. `More info <https://en.wikipedia.org/wiki/Data_migration>`__.

    notebook
        This refers to :term:`IPython Notebook`. More specifically, in the context of Websauna, the :doc:`the IPython Notebook shell you can open through the website <../narrative/misc/notebook>`.

    Paste
      A Python framework for building web applications on the top of `WSGI protocol <https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface>`__. See `Paste documentation <https://pypi.python.org/pypi/Paste>`__ .

    pcreate
      A command line command for creating new packages based on :term:`Pyramid` framework. `More info <http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/project.html>`__.

    persistent
        Something written on a disk e.g. it doesn't disappear when power goes down or the computer is restarted.

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

    production
        The production environment is also known as live, particularly for servers, as it is the environment that users directly interact with. :doc:`Websauna production configuration <../reference/config>`. `More information <https://en.wikipedia.org/wiki/Deployment_environment#Production>`__.

    Redis
        Redis is an open source (BSD licensed), in-memory data structure store, used as database, cache and message broker. It supports data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs and geospatial indexes with radius queries. `More information <http://redis.io/>`__.

    renderer
        A view callable needn't always return a Response object. If a view happens to return something which does not implement the Pyramid Response interface, Pyramid will attempt to use a renderer to construct a response. Usually renderer is a template name. The template engine loads this template and passes the view return value to it as template context. `More information <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html/>`__.

    resource
        In :term:`traversal` resource class presents one path part of the hierarchy. More information in :doc:`traversal documentation <../narrative/frontend/traversal>`

    sanity check
        Sanity check is a Websauna feature which prevents starting up a website in a state where Python code is inconsistent with databases. It checks all databases are up and models are correctly declared in the database. See :ref:`websauna.sanity_check` setting for more info.

    scaffold
        A project skeleton which generates a starting point for your application. Websauna uses `Pyramid scaffolding <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/scaffolding.html>`__ for its ``websauna_app`` and ``websauna_addon`` scaffols.

    secrets
        The secrets are passwords, API keys and other sensitive data which you want to avoid exposing. They are usually stored separately from the source code tree. Websauna has best practices how to store your secrets. See :ref:`secrets` in configuration documentation.

    Sentry
        Sentry is the modern error logging and aggregation platform for production servers. It allows you easily set alerts when errors start appear in :term:`production`. `More information <https://docs.getsentry.com/hosted/>`__.

    session fixation
        Session Fixation is an attack that permits an attacker to hijack a valid user session. The attack explores a limitation in the way the web application manages the session ID, more specifically the vulnerable web application. When authenticating a user, it doesn’t assign a new session ID, making it possible to use an existent session ID. `More information <https://www.owasp.org/index.php/Session_fixation>`__.

    slug
        Slug is a descriptive part of the URL that is there to make URL more (human) readable.
        `More information <http://stackoverflow.com/questions/427102/what-is-a-slug-in-django>`__.

    SQLAlchemy
        SQLAlchemy enables effortless SQL data manipulation from Python programming.

        SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. It provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language. `More information <http://www.sqlalchemy.org/>`__.

    staging
        Staging site, in website design, is a website used to assemble, test and review its newer versions before it is moved into production. This phase follows the development phase. The staging phase of the software life-cycle is often tested in an environment (hardware and software) that mirrors that of the production environment. :doc:`Websauna staging configuration <../reference/config>`. `More information <https://en.wikipedia.org/wiki/Staging_site>`__.

    state management
        :term:`SQLAlchemy` database session keeps automatically track of objects you have modified.
        `More information <http://docs.sqlalchemy.org/en/latest/orm/session_state_management.html>`__.


    testing
        Testing is the development face when automated test suite is executed against your application. See :ref:`test.ini` configuration reference. See :doc:`How to write and run tests <../narrative/testing/writing>`.

    URL dispatch
        A method of mapping URLs to views through regular expression. `See full documentation in Pyramid documentation. <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/urldispatch.html>`__.

    UUID
        A universally unique identifier (UUID) is an identifier standard used in software construction. A UUID is simply a 128-bit value. The meaning of each bit is defined by any of several variants. Websauna extensively uses UUID variant 4, which gives a value with 122-bit randomness. `More information <https://en.wikipedia.org/wiki/Universally_unique_identifier>`__.

    UTC
        Coordinated Universal, abbreviated as UTC, is the primary time standard by which the world regulates clocks and time. It is, within about 1 second, mean solar time at 0° longitude;[1] it does not observe daylight saving time. `More information <https://en.wikipedia.org/wiki/Coordinated_Universal_Time>`__.

    view
        A "view callable" is a callable Python object which is associated with a view configuration; it returns a response object. A view callable accepts a single argument: request, which will be an instance of a :term:`request` object. An alternate calling convention allows a view to be defined as a callable which accepts a pair of arguments: context object and :term:`request`: this calling convention is useful for traversal-based applications in which a context is always very important. A view callable is the primary mechanism by which a developer writes user interface code within :term:`Pyramid`. See :doc:`view documentation for more information <../narrative/frontend/views>`.

    virtual environment
        An isolated environment (folder) where all installed Python packages go. Each project should have its own virtual environment, so that different project dependencies do not mess up each other. `Read more <https://packaging.python.org/en/latest/installing.html>`__.