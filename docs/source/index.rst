Websauna's documentation
========================

Welcome to Websauna, a full stack Python application framework.

.. note::

    This is a work in progress project and documentation. There is no official release yet.


`Documentation <https://websauna.org/docs>`_ (`download as offline e-book <https://websauna.org/Websauna.epub>`_).

`Installation <https://websauna.org/docs/tutorials/gettingstarted/index.html>`_.

`Chat <https://websauna.org/docs/narrative/contributing/community.html#chat>`_.

`GitHub repository <https://github.com/websauna/websauna>`_.


Table of contents
=================

.. toctree::
    :maxdepth: 1

    narrative/background/index
    tutorials/gettingstarted/index
    narrative/local-development/index
    narrative/modelling/index
    narrative/crud/index
    narrative/view/index
    narrative/frontend/index
    narrative/form/index
    narrative/user/index
    narrative/testing/index
    narrative/misc/index
    tutorials/deployment/index
    narrative/ops/index
    narrative/contributing/index
    narrative/faq/index
    reference/index
    api/index


What it is?
===========

Websauna is a Python package and application framework for developing custom consumer and business web services. It emphasises meeting business requirements with reliable delivery times, responsiveness, consistency in quality, security and high data integrity. A low learning curve, novice friendliness and polished documentation help less seasoned developers to get their first release out quickly.

`Websauna project is open source (MIT) and on GitHub <http://github.com/websauna/websauna>`_.

How it is done?
===============

Build fast, reach high
----------------------

Websauna stands on the shoulders of `Python programming language <https://python.org>`_ and `Pyramid web framework <http://docs.pylonsproject.org/projects/pyramid/en/latest/>`_. It uses `SQLAlchemy <http://sqlalchemy.org/>`_ modelling for data and business logic with automatic admin interface generation. Polished integration, project scaffold and getting started tutorial allow a seasoned Python developer to roll out a custom web service within few hours - being a turn key solution for the first prototype that can be later iterated on.

Security
--------

Websauna has a strong drive for security. It is designed to be immune for OWASP top 10 vulnerabilities. Websauna heavily leans on optimistic concurrency control eliminating potential for race condition errors. ACID guarantees are followed through the codebase, making Websauna ideal for financial services needing high data integrity.

User experience and frontend
----------------------------

A default mobile friendly Bootstrap frontend is provided for landing page and form styling. This makes it possible to use ready premium theme packages for distinct user experience even if there is graphical design talent in a team. Federated authentication, like Facebook or Google login, is supported out of the box. Building RESTful behavior over business logic is made easy, so that frontend may be replaced with a heavier JavaScript solution when needed.

Data analysis
-------------

`IPython Notebook <http://ipython.org/>`_, an award winning data analysis and science tool, is directly integrated to Websauna. Analyzing website data and building interactive visualizations is within a reach of one click.

Modular architecture
--------------------

All default stack choices are suggestive, thus leaving room for opinions for different components and a path to scale up a service. There is no inversion of control - the developer is always in the driver's seat. A strong decoupling is achieved through component architecture, event dispatch and standardized addon mechanism. This allows building non-monolithic packages and frictionless distribution of work among teams.

When to use it?
===============

Websauna is focused on Internet facing sites where you have a public or private sign up process and a administrative back office. It's sweet spots are custom business portals and software-as-a-service sites which are too specialized for off-the-shelf solutions. Websauna is ideal for Internet startups that iterate fast and may face urgent scalability needs.
