============
Introduction
============

Welcome to Websauna, a full stack Python web framework for building consumer and community oriented websites.

.. contents:: :local:

What is it?
===========

Websauna gives you building blocks for creating scalable, state-of-art websites and services. Websauna gives a framework for efficient business problem solving, so that developers can maximize their productivity from day zero. It has a default opinion on all parts of the software stack to have a red line what to follow to get the first version out. This is done without sacrificing the flexibility, so that experienced developers can chose more optimized components for their specific needs.

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

When you write a database model, you usually need to have the basic create-read-update-delete (CRUD) cycle for them. Websauna can automatically generate most of this administrative interface for you, minimizing the effort needed for writing repeative form handling tasks. Furthermore Websauna is not limited to one admin interface, but can have different admins available for different users, and tries to hard to make sure that admin views are extensible and flexible.

Zero globals
------------

There are no global variables, non-overrideable parts or assumed behavior. All parts of the framework can be customized and the developer is always on the driving seat.

Security
--------

A special focus has been on making the framework secure and tolerate against human errors. The framework shields developers against TOP 10 OWASP vulnerabilities like SQL injection, cross site scripting and race conditions. Best practices exist for handling secrets like API tokens.

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

* **Least resistance**: When compromises and choices between components are made, a path of least resistance is preferred. This usually means picking up a choice most developers feel comfortable with.

* **Always provide a solution**: Make sure that persons armed with basic knowledge finds an answer to every of their question to get the first version of the site out.

Default stack
=============

Websauna suggests the following set of components to build the first version of a website. These are not set for the stone, but well tested, document and covered by tools. If you know better and you know your project requirements you are free to mix and match with more suitable options.

Backend
-------

* Python 3.5+

* Pyramid web framework

* PostgreSQ with JSONB support persistent data

* Redis for session and transient data

* Nginx web server

* uWSGI application server

Frontend
--------

* Bootstrap CSS ja JS frontend framework

* Jinja 2 templates

* Deform form framework with Colander schemas

* jQuery

* FontAwesome icons

