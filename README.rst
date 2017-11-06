Websauna is a full stack Python web framework for building web services and back offices with admin interface and sign up process.

.. |ci| image:: https://img.shields.io/travis/websauna/websauna/master.svg?style=flat-square
    :target: https://travis-ci.org/websauna/websauna/

.. |cov| image:: https://codecov.io/github/websauna/websauna/coverage.svg?branch=master
    :target: https://codecov.io/github/websauna/websauna?branch=master

.. |latest| image:: https://img.shields.io/pypi/v/websauna.svg
    :target: https://pypi.python.org/pypi/websauna/
    :alt: Latest Version

.. |license| image:: https://img.shields.io/pypi/l/websauna.svg
    :target: https://pypi.python.org/pypi/websauna/
    :alt: License

.. |versions| image:: https://img.shields.io/pypi/pyversions/websauna.svg
    :target: https://pypi.python.org/pypi/websauna/
    :alt: Supported Python versions

+-----------+-----------+-----------+
| |versions|| |latest|  | |license| |
+-----------+-----------+-----------+
| |ci|      | |cov|     |           |
+-----------+-----------+-----------+

.. image:: https://websauna.org/theme/images/logo-768.png

.. contents:: :local:

Introduction
============

Websauna is a Python web framework for developing highly customized consumer and business websites and backends. It emphasises a low learning curve, community friendliness and polished documentation, so that newcomer developers get their first release out quickly. This is done without sacrificing scalability and high maintainability for more complex websites. Websauna builds its foundation on best practices and innovation that web development and Python communities have been refining for the last 20 years.

Websauna is created with `modern Python 3 features <https://websauna.org/docs/narrative/misc/typing.html>`_, `Pyramid <https://websauna.org/docs/reference/glossary.html#term-pyramid>`_ web routing framework and `SQLAlchemy <https://websauna.org/docs/reference/glossary.html#term-sqlalchemy>`_ object relational mapping. You get out of the box user experience with `Jinja templates <https://websauna.org/docs/reference/glossary.html#term-jinja>`_ and `Bootstrap theming <https://websauna.org/docs/reference/glossary.html#term-bootstrap>`_, but you are free to bring in your own frontend.

Software development is only half of the story. Websauna additionally provides a basic deployment and operations story based on `Ansible <https://websauna.org/docs/reference/glossary.html#term-ansible>`_ automation.

Links
=====

* `Website <https://websauna.org/>`_

* `Getting started and installation <https://websauna.org/docs/tutorials/gettingstarted/index.html>`_

* `Chat <https://websauna.org/docs/narrative/contributing/community.html>`_ - It always pays off to ask first!

* `Documentation <https://websauna.org/docs>`_

* `Twitter <https://twitter.com/websauna9000>`_

* `Github <https://github.com/websauna/websauna>`_

When to use it?
===============

Websauna is focused on Internet facing sites where you have a public or private sign up process and an administrative interface. Its sweet spots include  custom business portals and software-as-a-service products which are too specialized for off-the-shelf solutions. Websauna is ideal for Internet startups that iterate fast and may face urgent scalability needs. Furthermore, you can easily integrate different frontends like React, Angular and mobile apps with Websauna back office.

What makes Websauna different?
==============================

Build fast, reach high
----------------------

Websauna application comes with default `admin interface <https://websauna.org/docs/narrative/crud/admin.html>`_ and `user sign up <https://websauna.org/docs/narrative/user/index.html>`_. You can start immediately developing business logic by adding `models <https://websauna.org/docs/narrative/modelling/models.html>`_, `views <https://websauna.org/docs/narrative/view/index.html>`_, `forms <https://websauna.org/docs/narrative/form/index.html>`_ and `CRUD controllers <https://websauna.org/docs/narrative/crud/crud.html>`_.

Polished integration, `getting started tutorial <https://websauna.org/docs/tutorials/gettingstarted/index.html>`_ and `project scaffolding <https://websauna.org/docs/narrative/misc/scaffolds.html>`_ allow a seasoned Python developer to roll out a custom web service within few a hours - being a turn key solution for the first prototype that can later be iterated on.

Websauna default stack choices are made high scalability in mind, so that your website can reach millions of users before you start hitting limitations. For example, `delayed and asynchronous tasks <https://websauna.org/docs/narrative/misc/task.html>`_ ensure your site stays responsive and can scale horizontally.

Bullet proof security
---------------------

Websauna is a security first solution . Its foundation principles make it immune to `OWASP top 10 vulnerabilities <https://www.owasp.org/index.php/OWASP_Top_Ten_Cheat_Sheet>`_. Websauna leans heavily on `optimistic concurrency control <https://websauna.org/docs/narrative/modelling/occ.html>`_ eliminating potential for race condition errors. `ACID guarantees <https://websauna.org/docs/reference/glossary.html#term-acid>`_ are followed throughout the codebase, making Websauna ideal for financial services needing high data integrity.

Great user experience out of the box
------------------------------------

A default mobile friendly Bootstrap frontend is provided for landing page and form styling. `You can drop in premium theme packages for distinct user experience <https://websauna.org/docs/narrative/frontend/themes.html>`_  even if there is graphical design talent in your team. Federated authentication, like `Facebook <https://websauna.org/docs/narrative/user/oauth.html#setting-up-facebook-login>`_ or `Google login <https://websauna.org/docs/narrative/user/oauth.html#setting-up-google-login>`_, is supported out of the box. Building RESTful behavior over business logic is made easy, so that frontend may be replaced with a heavier JavaScript solution when needed.

Creating an ecosystem with addons and choices
---------------------------------------------

All default stack choices are suggestive, thus leaving room for opinions for different components and a path to scale up a service. There is no inversion of control - the developer is always in the driver's seat. A strong decoupling is achieved through component architecture, event dispatch and `standardized addon mechanism <https://websauna.org/docs/narrative/misc/scaffolds.html#websauna-addon>`_. This allows building non-monolithic packages and frictionless distribution of work among teams.

`You can browse available addons on Github <https://github.com/websauna/>`_.

Deployment has never been this easy
-----------------------------------

A significant part of software development work is maintaining and updating services. Websauna provides `a default deployment story <https://websauna.org/docs/tutorials/deployment/index.html>`_ using `Ansible <https://websauna.org/docs/reference/glossary.html#term-ansible>`_. When your website is ready to go live, you point the Ansible playbook to any Linux installation and it will deploy a fully functional website within a few minutes. The deployment choices are made by security experts for your convenience, so that even without deep sysadmin knowledge you can run your sites securely.

Because Websauna uses vendor neutral Ansible playbooks, you are not tied to a particular provider. Migrating between service providers is easy. You can run Websauna on Amazon, Azure, Hetzner, Digital Ocean, Linode, Upcloud or any other cloud server provider.

Open the shell prompt of the future
-----------------------------------

Websauna comes with `integrated IPython Notebook support <https://websauna.org/docs/narrative/misc/notebook.html>`_.
`IPython Notebook <https://websauna.org/docs/reference/glossary.html#term-ipython>`_, an award winning data analysis and science tool, is directly integrated into Websauna. You can open a browser based shell prompt within your admin site with one click.

The IPython integration makes Websauna ideal for science and data analysis use cases. You can also use the administrative shell for ad hoc system administration tasks and data fixes.
