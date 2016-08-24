============
Introduction
============

Welcome to Websauna, a full stack Python web framework for building consumer and community oriented websites.

.. contents:: :local:

What is it?
===========

Websauna gives you building blocks for creating scalable, state-of-the-art websites and services. The framework enables  efficient business problem solving, so that developers can maximize productivity from day zero. Websauna is suggestive and has default options on all parts of stack, so one can follow a red line to get the first release out quickly. On the other hand, Websauna does not enforce hard opinions and sacrifice flexibility, so that experienced developers can easily override parts and use more sophisticated components for specific needs.

Websauna achieves flexibility by keeping its own codebase minimal and not reinventing the wheel. Instead it provides a polished integration of the top packages of Python ecosystem like :term:`Pyramid` web framework, :term:`SQLAlchemy` object relationship mapper, :term:`Alembic` migration scripts, :term:`IPython` shell, :term:`Authomatic` federated login, :term:`Jinja` templating and :term:`pytest` testing framework.

Websauna is focused on Internet facing sites where you have a public or private sign up process and administrative backend. It's sweet spots are custom business portals, software-as-a-service sites and consumer portals. A special focus is given for security, so that Websauna is a strong candidate for financial technology and eCommerce solutions.

Features
========

Functional site out of box
--------------------------

The default project scaffold provides a working website with sign up and login. Developers can focus building value adding business features from a day zero.

Vetted default stack
--------------------

Websauna provides a default choice for every stack component vetted by the most experienced Python and web developers of the world. The framework is guaranteed to work these components with high quality integration guides, so that novice developers can pick up speed and time to deploy is fast. However there always exist a layer of abstraction, when the scalability needs arise, all components can be replaced.

Responsive load times
---------------------

Websauna runs on Pyramid micro framework - a HTTP request routing engine known for its high performance. By supporting asynchronous and scheduled task out of the box blocking operations like sending out email and or calling third party APIs can be handled outside the HTTP request processing. The framework supports intelligent cache and CDN configurations making it easy to optimize load static asset times. Jinja templates are compiled to Python bytecode for minimal HTML throughput delay.

Responsive design
-----------------

The default website templates are mobile first, based on Bootstrap, the most popular HTML, CSS, and JS framework for developing responsive, mobile first projects on the web. The site default theme and forms follow Boostrap best practices, but you are free to drop in your own frontend.

Automatic admin interface
-------------------------

When you write a database model, you usually need to have the basic create-read-update-delete (CRUD) cycle for them. Websauna can automatically generate most of this administrative interface for you, minimizing the effort needed for writing repeative form handling tasks. Furthermore Websauna is not limited to one admin interface, but can have different admins available for different users, and tries hard to make sure that admin views are extensible and flexible.

IPython Notebook integration
----------------------------

Open a powerful IPython Notebook shell at your site with a single click. IPython is a popular tool in data analysis and scientific work. It provides powerful number crunching capabilities and graph plotting. Furthermore it can act as a modern shell for maintenance and one shot style tasks which are often performed from server Python prompt.

Zero globals
------------

There are no global variables, non-overrideable parts or assumed behavior. All parts of the framework can be customized and the developer is always on the driving seat.

Security
--------

A special focus has been on making the framework secure and tolerate against human errors. The framework shields developers against TOP 10 OWASP vulnerabilities like SQL injection, cross site scripting and race conditions. Best practices exist for handling secrets like API tokens.

Database management and migration
---------------------------------

Websauna provides tools for automatic and manual database migrations and backup. Migration scripts are package specific, making it possible to build non-monolithic applications with packages with independent life cycle.

High quality documentation
--------------------------

The documentation is the business card of an open source project. Websauna has no question left unanswered policy, covering all aspects of software development and devops, so that developers can independently learn and apply the framework.

Type hinting
------------

Websauna supports Python 3.5 type hinting. This makes it plays nicely with autocompletion, code insight and boosts developer productivity. With type hinting, the editor can be smart about the written code and red line mistakes while you are typing them.

Optimistic concurrency control
------------------------------

Handling concurrency is non-trivial matter. The framework supports optimistic concurrency control with atomic requests, so that the developer is freed from the cognitive load of manual lock handling. This leads to less hard to manage race condition issues.

Extensibility
-------------

There exist a default addon scaffold and extension mechanism, making it possible to build reusable modules and ecosystem around Websauna core.

Design goals
============

* **Integrate, not develop**: Websauna does not try to invent anything itself. It takes a set of components and best practices vetted by the best developers and makes them to easily adoptable package.

* **Always a solution**: Make sure that persons armed with basic knowledge finds an answer to every of their question to get the first version of the site out.

* **Least resistance**: When compromises and choices between default components are made, a path of least resistance is preferred. This usually means picking up a choice most developers feel comfortable with.

Default stack
=============

Websauna suggests the following set of components to build the first version of a website. These are not set for the stone, but well tested, document and covered by tools. If you know better and you know your project requirements you are free to mix and match with more suitable options.

Backend
-------

* Python 3.4+

* Pyramid web framework

* PostgreSQL with JSONB support persistent data

* Redis for session and transient data

* Nginx web server

* uWSGI application server

Frontend
--------

* :term:`Bootstrap` frontend framework for CSS and JavaScript

* :term:`Jinja` templates

* :term:`Deform` form framework

If you need something else
==========================

If you are looking for a content management system check out Kotti CMS and Substance D. If you need for a stock eCommerce site check out Shopify.
