.. _glossary:

Glossary
========

Many glossary descrpitions are taken from `Wikipedia <https://en.wikipedia.org/>`__.

.. glossary::
    :sorted:

    ACID
        In computer science, ACID (Atomicity, Consistency, Isolation, Durability) is a set of properties that guarantee that database transactions are processed reliably. `More info <https://en.wikipedia.org/wiki/ACID>`__.

    ACL
        An access control list (ACL), with respect to a computer file system, is a list of permissions attached to an object. An ACL specifies which users or system processes are granted access to objects, as well as what operations are allowed on given objects. `Read about ACL in Pyramid <http://docs.pylonsproject.org/projects/pyramid/en/1.0-branch/narr/security.html#elements-of-an-acl>`__.

    admin
        The admin section of a Websauna site. Logged in users with admin privileges can go to this section and see and edit all the site data. :doc:`Read Websauna admin documentation <../narrative/crud/admin>`.

    Alembic
       A migration script tool for :term:`SQLAlchemy`. `More info <http://alembic.readthedocs.org/>`__.

    Ansible
        Ansible is an IT automation tool. It can configure systems, deploy software, and orchestrate more advanced IT tasks such as continuous deployments or zero downtime rolling updates. `More information <http://www.ansible.com/>`__.

    Arrow
        Arrow is a Python library that offers a sensible, human-friendly approach to creating, manipulating, formatting and converting dates, times, and timestamps. It implements and updates the datetime type, plugging gaps in functionality, and provides an intelligent module API that supports many common creation scenarios. Simply put, it helps you work with dates and times with fewer imports and a lot less code. `More information <http://crsmithdev.com/arrow/>`__.

    Authomatic
        Authomatic is a framework agnostic library for Python web applications with a minimalistic but powerful interface which simplifies authentication of users by third party providers like Facebook or Twitter through standards like OAuth and OpenID. `More info <http://peterhudec.github.io/authomatic/>`__.

    Base64
        Base64 is a group of similar binary-to-text encoding schemes that represent binary data in an ASCII string format by translating it into a radix-64 representation. More information `<https://en.wikipedia.org/wiki/Base64>`__.

    Bootstrap
        Bootstrap is the most popular HTML, CSS, and JS framework for developing responsive, mobile first projects on the web. `More informatin <http://getbootstrap.com/>`__.

    CDN
        A content delivery network or content distribution network (CDN) is a globally distributed network of proxy servers deployed in multiple data centers. The goal of a CDN is to serve content to end-users with high availability and high performance. Many CDNs allow developers to upload their own static asset files to speed up their loading. `More information <https://en.wikipedia.org/wiki/Content_delivery_network>`__.

    Celery
        Celery a task queue for Python with focus on real-time processing, while also supporting task scheduling. `More info <http://celery.readthedocs.org/>`__.

    chromedriver
        WebDriver is an open source tool for automated testing of webapps across many browsers. Used in Websauna to control functional tests with :term:`Splinter` and :term:`Selenium`. `More information <https://sites.google.com/a/chromium.org/chromedriver/>`__.

    Colander
        A simple schema-based serialization and deserialization library. Useful for building forms, RESTFul APIs and other interfaces where you need to transform and validate data. `More information <https://pypi.python.org/pypi/colander>`__.

    colanderalchemy
        A Python package to generate :term:`Colander` forms from :term:`SQLAlchemy` models. `More information <https://pypi.python.org/pypi/ColanderAlchemy>`__.

    cookiecutter
        A Python package to create projects and packages from project templates. `More information <https://pypi.python.org/pypi/cookiecutter>`__.

    CRUD
        In computer programming, create, read, update and delete, sometimes called SCRUD with an "S" for Search, are the four basic functions of persistent storage. :doc:`Read about CRUD in Websauna <../narrative/crud/crud>`.
        `More info <https://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`__.

    CSRF
        Cross-site request forgery, also known as one-click attack or session riding and abbreviated as CSRF (sometimes pronounced sea-surf) or XSRF, is a type of malicious exploit of a website where unauthorized commands are transmitted from a user that the website trusts. :doc:`See Websauna CSRF protection documentation <../narrative/form/csrf>`. `More info <https://en.wikipedia.org/wiki/Cross-site_request_forgery>`__.

    CSS
        Cascading Style Sheets (CSS) is a style sheet language used for describing the presentation of a document written in a markup language. It's most often used to set the visual style of web pages and user interfaces written in HTML and XHTML. `More info <https://en.wikipedia.org/wiki/Cascading_Style_Sheets>`__.

    database
        A database is an organized collection of data. A database management system (DBMS) is a computer software application that interacts with the user, other applications, and the database itself to capture and analyze data. A general-purpose DBMS is designed to allow the definition, creation, querying, update, and administration of databases. Websauna defaults to :term:`PostgreSQL` DBMS.

    development
        Development is the stage of the deployment when the developer is locally working on the code on a local machine. See :ref:`development.ini`.

    development.ini
      The default configuration file when you run Websauna on your local computer when doing development. For more information see :doc:`configuration <../reference/config>`.

    deform
        A form framework suggested by Websauna. :doc:`Read Websauna form documentation <../narrative/form/form>`. `See widget samples <http://demo.substanced.net/deformdemo/>`__. `More info <http://deform.readthedocs.org/en/latest/>`__.

    duplicity
        Duplicity backs directories by producing encrypted tar-format volumes and uploading them to a remote or local file server. Because duplicity uses librsync, the incremental archives are space efficient and only record the parts of files that have changed since the last backup. Because duplicity uses GnuPG to encrypt and/or sign these archives, they will be safe from spying and/or modification by the server. `More info <http://duplicity.nongnu.org/>`__.

    DOM
        The Document Object Model (DOM) is a cross-platform and language-independent convention for representing and interacting with objects in parsed HTML, XHTML, and XML documents. The nodes of every document are organized in a tree structure, called the DOM tree. Objects in the DOM tree may be addressed and manipulated by using methods on the objects. The public interface of a DOM is specified in its application programming interface (API). `More information <https://en.wikipedia.org/wiki/Document_Object_Model>`__.

    DoS
        In computing, a denial-of-service (DoS) attack is an attempt to make a machine or network resource unavailable to its intended users, such as to temporarily or indefinitely interrupt or suspend services of a host connected to the Internet. A distributed denial-of-service (DDoS) is where the attack source is more than one–and often thousands of-unique IP addresses. `More information <https://en.wikipedia.org/wiki/Denial-of-service_attack>`__.

    Font Awesome
        A popular web icon library distributed as web fonts to allow :term:`CSS` coloring options. `More information <http://fontawesome.io/>`__.

    git
      The most popular version control software at the moment. `More info <https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control>`__.

    .gitignore
      A mechanism to avoid placing files under a git version control by blacklisting them.

    htpasswd
        .htpasswd is a flat-file used to store usernames and password for basic authentication on an Apache HTTP Server and others. `More info <https://en.wikipedia.org/wiki/.htpasswd>`__.

    Initializer
        Initializer is the main entry point of your Websauna application. It is a class responsible for ramping up and integrating various subsystems. For more information see :py:class:`websauna.system.Initializer`.

    INI
        he INI file format is an informal standard for configuration files for some platforms or software. INI files are simple text files with a basic structure composed of sections, properties, and values. `More info <https://en.wikipedia.org/wiki/INI_file>`__.

    IPython
        Next generation read–eval–print loop engine for Python and other programming languages. See `IPython Notebook site <http://ipython.org/notebook.html>`__ for more information. See also :term:`IPython Notebook`.

    IPython Notebook
        A powerful browser based shell for a Python. Popular in scientific community and data analysis. See `IPython Notebook site <http://ipython.org/notebook.html>`__ for more information.

    HTML
        HyperText Markup Language, commonly referred to as HTML, is the standard markup language used to create web pages. Along with :term:`CSS`, and :term:`JavaScript`, HTML is a cornerstone technology, used by most websites to create visually engaging webpages, user interfaces for web applications, and user interfaces for many mobile applications. `More information <https://en.wikipedia.org/wiki/HTML>`__.

    isolation level
        How database handles transactions where there is a :term:`race condition`. See also :term:`ACID`.

    JavaScript
        JavaScript is a high-level, dynamic, untyped, and interpreted programming language. It has been standardized in the ECMAScript language specification. Alongside :term:`HTML` and :term:`CSS`, it is one of the three essential technologies of World Wide Web content production; the majority of websites employ it and it is supported by all modern web browsers without plug-ins. `More information <https://en.wikipedia.org/wiki/JavaScript>`__.

    Jinja
        Jinja2 is a modern and designer-friendly templating language for Python, modelled after Django’s templates. It is fast, widely used and secure with the optional sandboxed template execution environment. `Read more <http://jinja.pocoo.org/docs/dev//>`__.

    JSON
        JSON, JavaScript Object Notation, specified by RFC 7159 and by ECMA-404, is a lightweight data interchange format inspired by JavaScript object literal syntax. Most web related programming languages and support JSON as an exchange format. `Read more <https://en.wikipedia.org/wiki/Json/>`__.

    JSONB
        A :term:`PostgreSQL` column type to store JSON structured data. `Read more <https://www.compose.io/articles/is-postgresql-your-next-json-database/>`__.

    Less
        Less is a :term:`CSS` pre-processor, meaning that it extends the CSS language, adding features that allow variables, mixins, functions and many other techniques that allow you to make CSS that is more maintainable, themable and extendable. `Read more <http://lesscss.org/>`__.

    Mandrill
        Mandrill is a reliable, scalable, and secure delivery API for transactional emails from websites and applications. It's ideal for sending data-driven transactional emails, including targeted e-commerce and personalized one-to-one messages. `More information <http://mandrill.com/>`__.

    mock
        Using mock allows you to replace parts of your system under test with mock objects and make assertions about how they have been used. In :term:`Python` this is done using `Mock library <https://pypi.python.org/pypi/mock>`__.

    model
        A model is a Python class describing :term:`persistent` data structure. A model provides convenient Python API to manipulate your data, so that save and load it into a :term:`database`. :doc:`More information <../narrative/modelling/models>`.

    migration
        Data migration refers to procedure of changing how data is stored in your database - adding new data columns or changing how old columns behave. It is usually performed one time batch operation per database. Read :doc:`Websauna migrations documentation <../narrative/ops/migrations>`. `More info <https://en.wikipedia.org/wiki/Data_migration>`__.

    Nginx
        NGINX is a free, open-source, high-performance HTTP server and reverse proxy, as well as an IMAP/POP3 proxy server. NGINX is known for its high performance, stability, rich feature set, simple configuration, and low resource consumption. `More information <https://www.nginx.com/>`__.

    notebook
        This refers to :term:`IPython Notebook`. More specifically, in the context of Websauna, the :doc:`the IPython Notebook shell you can open through the website <../narrative/misc/notebook>`.

    OAuth
        OAuth is an open standard for authorization, commonly used as a way for Internet users to log into third party websites using their Microsoft, Google, Facebook or Twitter accounts without exposing their password. `More information <https://en.wikipedia.org/wiki/OAuth>`__.

    optimistic concurrency control
        Optimistic concurrency control (OCC) is a concurrency control method applied to transactional systems such as relational database management systems and software transactional memory. OCC assumes that multiple transactions can frequently complete without interfering with each other. While running, transactions use data resources without acquiring locks on those resources. Before committing, each transaction verifies that no other transaction has modified the data it has read. If the check reveals conflicting modifications, the committing transaction rolls back and can be restarted. `More information <https://en.wikipedia.org/wiki/Optimistic_concurrency_control>`__.

    Paste
      A Python framework for building web applications on the top of `WSGI protocol <https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface>`__. See `Paste documentation <https://pypi.python.org/pypi/Paste>`__ .

    pcreate
      A command line command for creating new packages based on :term:`Pyramid` framework. `More info <http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/project.html>`__.

    persistent
        Something written on a disk e.g. it doesn't disappear when power goes down or the computer is restarted.

    pip
      A Python package installation command. `Read more <https://packaging.python.org/en/latest/installing.html>`__.

    playbook
        Playbooks are Ansible’s configuration, deployment, and orchestration language. They can describe a policy you want your remote systems to enforce, or a set of steps in a general IT process. `Read more <http://docs.ansible.com/ansible/playbooks.html>`__.

    Postfix
        Postfix attempts to be fast, easy to administer, and secure mail server. `More information <http://www.postfix.org/>`__.

    Pyramid
        Low level web framework Python doing request routing, configuration, sessions and such. See `Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/introduction.html>`__.

    pyramid_celery
        A Celery integration for Pyramid. `More info <https://github.com/sontek/pyramid_celery>`__.

    pyramid_debugtoolbar
        A package to collect and show various debug and diagnose information from a local Pyramid development server. `More info <http://docs.pylonsproject.org/projects/pyramid-debugtoolbar/en/latest/>`__.

    pyramid_notebook
        Open :term:`IPython Notebook` directly from :term:`Pyramid` website. `More info <https://pypi.python.org/pypi/pyramid-notebook/>`__.

    pytest
        pytest is a mature full-featured Python testing tool that provides easy no-boilerplate testing, scales from simple unit to complex functional testing and integrates with other testing methods and tools. `More information <https://en.wikipedia.org/wiki/Deployment_environment#Production>`__.

    pytest-splinter
        :term:`Splinter` integration for :term:`pytest` based test suites. `More information <https://github.com/pytest-dev/pytest-splinter>`__.

    Python
        Python is a programming language that lets you work quickly and integrate systems more effectively. `Learn more <https://www.python.org/>`__.

    PostgreSQL
        The world's most advanced open source database. PostgreSQL is a powerful, open source object-relational database system. It has more than 15 years of active development and a proven architecture that has earned it a strong reputation for reliability, data integrity, and correctness. `More information <http://postgresql.org/>`__.

    production
        The production environment is also known as live, particularly for servers, as it is the environment that users directly interact with. :doc:`Websauna production configuration <../reference/config>`. `More information <https://en.wikipedia.org/wiki/Deployment_environment#Production>`__.

    race condition
        A race condition or race hazard is the behavior of an electronic, software or other system where the output is dependent on the sequence or timing of other uncontrollable events. It becomes a bug when events do not happen in the order the programmer intended. The term originates with the idea of two signals racing each other to influence the output first. `More information <https://en.wikipedia.org/wiki/Race_condition>`__.

    Redis
        Redis is an open source (BSD licensed), in-memory data structure store, used as database, cache and message broker. It supports data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs and geospatial indexes with radius queries. `More information <http://redis.io/>`__.

    renderer
        A view callable needn't always return a Response object. If a view happens to return something which does not implement the Pyramid Response interface, Pyramid will attempt to use a renderer to construct a response. Usually renderer is a template name. The template engine loads this template and passes the view return value to it as template context. `More information <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html/>`__.

    resource
        In :term:`traversal` resource class presents one path part of the hierarchy. More information in :doc:`traversal documentation <../narrative/view/traversal>`

    Robot Framework
        Robot Framework is a generic test automation framework for acceptance testing and acceptance test-driven development (ATDD). It has easy-to-use tabular test data syntax and it utilizes the keyword-driven testing approach. Its testing capabilities can be extended by test libraries implemented either with Python or Java, and users can create new higher-level keywords from existing ones using the same syntax that is used for creating test cases. `More information <http://robotframework.org/>`__.

    sanity check
        Sanity check is a Websauna feature which prevents starting up a website in a state where Python code is inconsistent with databases. It checks all databases are up and models are correctly declared in the database. See :ref:`websauna.sanity_check` setting for more info.

    scaffold
        A project skeleton which generates a starting point for your application. Websauna uses :term:`cookiecutter` as the tool to create it, using ``cookiecutter-websauna-app`` and ``cookiecutter-websauna-addon`` templates.

    secrets
        The secrets are passwords, API keys and other sensitive data which you want to avoid exposing. They are usually stored separately from the source code tree. Websauna has best practices how to store your secrets. See :ref:`secrets` in configuration documentation.

    Selenium
        Selenium automates browsers. That's it! What you do with that power is entirely up to you. Primarily, it is for automating web applications for testing purposes, but is certainly not limited to just that. Boring web-based administration tasks can (and should!) also be automated as well. `More information <http://www.seleniumhq.org/>`__.

    Sentry
        Sentry is the modern error logging and aggregation platform for production servers. It allows you easily set alerts when errors start appear in :term:`production`. `More information <https://docs.getsentry.com/hosted/>`__.

    session fixation
        Session Fixation is an attack that permits an attacker to hijack a valid user session. The attack explores a limitation in the way the web application manages the session ID, more specifically the vulnerable web application. When authenticating a user, it doesn’t assign a new session ID, making it possible to use an existent session ID. `More information <https://www.owasp.org/index.php/Session_fixation>`__.

    shared hosting
        Shared web hosting service refers to a web hosting service where many websites reside on one web server connected to the Internet. This is generally the most economical option for hosting, as the overall cost of server maintenance is amortized over many customers. `More information <https://en.wikipedia.org/wiki/Shared_web_hosting_service>`__.

    slug
        Slug is a descriptive part of the URL that is there to make URL more (human) readable.
        `More information <http://stackoverflow.com/questions/427102/what-is-a-slug-in-django>`__.

    SQL
        SQL is a special-purpose programming language designed for managing data held in a relational database management system (RDBMS). `More information <https://en.wikipedia.org/wiki/SQL>`__.

    SQLAlchemy
        SQLAlchemy enables effortless SQL data manipulation from Python programming.

        SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. It provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language. `More information <http://www.sqlalchemy.org/>`__.

    Splinter
        Splinter is an open source tool for testing web applications using Python. It lets you automate browser actions, such as visiting URLs and interacting with their items. `More information <http://splinter.readthedocs.org/>`__.

    SSH
        Secure Shell, or SSH, is a cryptographic (encrypted) network protocol to allow remote login and other network services to operate securely over an unsecured network. `More information <https://en.wikipedia.org/wiki/Secure_Shell>`__.

    SSH agent
        SSH is a protocol allowing secure remote login to a computer on a network using public-key cryptography. SSH client programs typically run for the duration of a remote login session and are configured to look for the user's private key in a file in the user's home directory (e.g., .ssh/id_rsa). For added security, it is common to store the private key in an encrypted form, where the encryption key is computed from a passphrase that the user has memorized. Because typing the passphrase can be tedious, many users would prefer to enter it just once per local login session. The most secure place to store the unencrypted key is in program memory, and in Unix-like operating systems, memory is normally associated with a process. A normal SSH client process cannot be used to store the unencrypted key because SSH client processes only last the duration of a remote login session. Therefore, users run a program called ``ssh-agent`` that runs the duration of a local login session, stores unencrypted keys in memory, and communicates with SSH clients using a Unix domain socket. . `More information <https://en.wikipedia.org/wiki/Ssh-agent>`__.


    staging
        Staging site, in website design, is a website used to assemble, test and review its newer versions before it is moved into production. This phase follows the development phase. The staging phase of the software life-cycle is often tested in an environment (hardware and software) that mirrors that of the production environment. :doc:`Websauna staging configuration <../reference/config>`. `More information <https://en.wikipedia.org/wiki/Staging_site>`__.

    state management
        :term:`SQLAlchemy` database session keeps automatically track of objects you have modified.
        `More information <http://docs.sqlalchemy.org/en/latest/orm/session_state_management.html>`__.

    Supervisor
        Supervisor is a client/server system that allows its users to monitor and control a number of processes on UNIX-like operating systems. It shares some of the same goals of programs like launchd, daemontools, and runit. Unlike some of these programs, it is not meant to be run as a substitute for init as “process id 1”. Instead it is meant to be used to control processes related to a project or a customer, and is meant to start like any other program at boot time.
        `More information <http://supervisord.org/>`__.

    TDD
        Test-driven development (TDD) is a software development process that relies on the repetition of a very short development cycle: first the developer writes an (initially failing) automated test case that defines a desired improvement or new function, then produces the minimum amount of code to pass that test, and finally refactors the new code to acceptable standards. `More information <https://en.wikipedia.org/wiki/Test-driven_development/>`__.

    test fixture
        The purpose of test fixtures is to provide a fixed baseline upon which tests can reliably and repeatedly execute. This pattern is extensively used by :term:`pytest`. `More information <http://pytest.org/latest/fixture.html>`__.

    testing
        Testing is the development face when automated test suite is executed against your application. See :ref:`test.ini` configuration reference. See :doc:`How to write and run tests <../narrative/testing/writing>`.

    Tox
        Tox is a generic virtualenv management and test command line tool you can use for: checking your package installs correctly with different Python versions and interpreters, running your tests in each of the environments, configuring your test tool of choice, acting as a frontend to Continuous Integration servers, greatly reducing boilerplate and merging CI and shell-based testing. `More information <https://pypi.python.org/pypi/tox>`__.

    transaction retry
        If a succesfully committed transaction is doomed by the database due to a :term:`race condition` the application tries to replay the HTTP request certain number of times before giving up. This usually works on the assumptions race conditions are rare and the data being modified does not need content locking like protection. See :term:`optimistic concurrency control`.

    URL dispatch
        A method of mapping URLs to views through regular expression. `See full documentation in Pyramid documentation. <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/urldispatch.html>`__.

    UUID
        A universally unique identifier (UUID) is an identifier standard used in software construction. A UUID is simply a 128-bit value. The meaning of each bit is defined by any of several variants. Websauna extensively uses UUID variant 4, which gives a value with 122-bit randomness. `More information <https://en.wikipedia.org/wiki/Universally_unique_identifier>`__.

    UTC
        Coordinated Universal, abbreviated as UTC, is the primary time standard by which the world regulates clocks and time. It is, within about 1 second, mean solar time at 0° longitude;[1] it does not observe daylight saving time. `More information <https://en.wikipedia.org/wiki/Coordinated_Universal_Time>`__.

    uWSGI
        The uWSGI project aims at developing a full stack for application servers for various programming languages. Protocols, proxies, process managers and monitors are all implemented using a common api and a common configuration style. `More information <https://uwsgi-docs.readthedocs.org/en/latest/#>`__.

    vault
        A vault is a generic term that refers to a file or a service that contains protected secrets, like passwords and private keys.

    view
        A "view callable" is a callable Python object which is associated with a view configuration; it returns a response object. A view callable accepts a single argument: request, which will be an instance of a :term:`request` object. An alternate calling convention allows a view to be defined as a callable which accepts a pair of arguments: context object and :term:`request`: this calling convention is useful for traversal-based applications in which a context is always very important. A view callable is the primary mechanism by which a developer writes user interface code within :term:`Pyramid`. See :ref:`views`.

    view mapper
        A view mapper is an object in :term:`Pyramid` that accepts a set of keyword arguments and which returns a callable. The returned callable is called with the view callable object. The returned callable should itself return another callable which can be called with the "internal calling protocol" (context, request). `Read more <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#using-a-view-mapper>`__.


    virtual environment
        An isolated environment (folder) where all installed Python packages go. Each project should have its own virtual environment, so that different project dependencies do not mess up each other. `Read more <https://packaging.python.org/en/latest/installing.html>`__.

    Waitress
        Waitress is meant to be a production-quality pure-Python WSGI server with very acceptable performance. It has no dependencies except ones which live in the Python standard library. It runs on CPython on Unix and Windows under Python 2.6+ and Python 3.2+. It is also known to run on PyPy 1.6.0+ on UNIX. It supports HTTP/1.0 and HTTP/1.1. `Read more <https://pypi.python.org/pypi/waitress>`__.

    WSGI
        The Web Server Gateway Interface (WSGI) is a specification for simple and universal interface between web servers and web applications or frameworks for the Python programming language. It was originally specified in PEP 333 authored by Phillip J. Eby, and published on 7 December 2003. It has since been adopted as a standard for Python web application development. The latest version of the specification is v1.0.1, also known as PEP 3333, published on 26 September 2010. `Read more <https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface>`__.
