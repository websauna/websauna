==========
Comparison
==========

Here is a comparison with Websauna and other popular Python frameworks.

.. contents:: :local:

Introduction
============

Websauna does not want to offer only a pile of Python code for the developers to play with - it wants to offer enough tools and integrated approach to cover the full website lifecycle.

Websauna does things differently as it...

* wants to offer a functional site out of the box

* does not make too tight couping between the components, like CRUD and models

* standardizes timed and asynchronous tasks

* extends framework to cover basic devops like backups

The modern web development is not simple having a script on the server which writes HTTP response on HTTP request read. The topics cover tasks like setting up servers, optimizing response times, balancing the load, handling operations securely. Websauna does not force its approaches upon the developers, but offers at least one solution to tackle each of the issues required for the full website life cycle management.

Frameworks
==========

Websauna
--------

A working website with sign in and sign up out of the box. Build the first version fast, but make sure the developer is on a driver's seat for iteratively scale up and replace components and parts of the stack.

Default template engine: :term:`Jinja`

Pyramid
-------

A small, fast, down-to-earth, open source. From developers to developers.

Default template engine: None

Django
------

Python Web framework that encourages rapid development and clean, pragmatic design.

Default template engine: Django

Flask
-----

Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions.

Default template engine: :term:`Jinja`

Comparison
==========

.. note ::

    The following table considers a feature present only if it's in the default project scaffold, core system and tutorials. Many frameworks may have these features as an addon, but require additional integration on the behalf of a developer.

.. raw:: html

    <div>
        Legend:
    </div>

    <style>
        .built-in {
            background: #afa;
        }

        .configurable {
            background: #ffa;
        }

        .addon {
            background: #ffa;
        }

        .integration-needed {
            background: #faa;
        }

        .not-there,
        .unopionated {
            background: #eee;
        }

        .no-data {
            background: #aaf;
        }

        .comparison {
            width: 100%;
        }

        .comparison td,
        .comparison th {
            vertical-align: top;
            border-top: 1px solid #aaa;
            padding: 5px;
        }

        .comparison th {
            text-align: right;
            max-width: 200px;
            font-size: 80%;

        }

        .comparison th h3 {
            text-align: left;
            padding: 20px 0;
        }

        .comparison thead th {
            text-align: center;
        }

    </style>

    <table class="comparison">
        <thead>
            <tr>
                <th>Subsystem</th>
                <th>Websauna</th>
                <th>Pyramid</th>
                <th>Django</th>
                <th>Flask</th>
            </tr>
        </thead>

        <tbody>

            <tr>
                <th colspan="5"><h3>Architechture</h3></th>
            </tr>

            <tr>
                <th>Batteries included approach</th>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>Free from global variables</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>Developer controlled entry points</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th>Components and services</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>Mixin and multi-inheritance heavy</th>
                <td class="not-there"></td>
                <td class="built-in"><sup><a href="#mixin">3</a></sup></td>
                <td class="not-there"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>Events</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th>Magic filenames and locations</th>
                <td class="not-there"></td>
                <td class="not-there""></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>URL dispatch</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th>Traversal</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>Type hinting</th>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="not-there"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Configuration and extensibility</h3></th>
            </tr>

            <tr>
                <th>Project scaffolding</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>


            <tr>
                <th>Linear application initialization</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="not-there"><sup><a href="#installed-apps">1</a></sup></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th>Extensible config files</th>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="not-there"><sup><a href="#settings-inclusion">2</a></sup></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>Support for configuration secrets</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Addon mechanism</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>HTTP request and response</h3></th>
            </tr>

            <tr>
                <th>Application-level middleware ("tweens")</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>


            <tr>
                <th>WSGI middleware</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th>Inline URL route declarations</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
            </tr>


            <tr>
                <th colspan="5"><h3>Templating</h3></th>
            </tr>

            <tr>
                <th>Default site page templates</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Default frontend framework</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Default 404 and 500</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Flash messages</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Database and modelling</h3></th>
            </tr>

            <tr>
                <th>SQL modelling</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Optimistic concurrency control</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>JSON/JSONB and schemaless data</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Migrations</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Transient data and caching</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Forms and CRUD</h3></th>
            </tr>

            <tr>
                <th>Form schemas</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Form autogeneration from models</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Themed forms</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>CRUD</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Widgets for SQL manipulation</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Admin</h3></th>
            </tr>

            <tr>
                <th>Automatically generated admin</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Shell and notebook</h3></th>
            </tr>

            <tr>
                <th>One click shell</th>
                <td class="built-in"><sup><a href="#mixin">4</a></sup></td></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Login and sign up</h3></th>
            </tr>

            <tr>
                <th>Default login</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Default sign up</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Federated authentication (Facebook et. al.)</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Security</h3></th>
            </tr>

            <tr>
                <th>Access control lists and permission hierarchy</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>Forbid CSRF'ed POST by default</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Throttling</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Non-guessable IDs</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Race condition mitigation</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Secrets and API token management</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Responsiveness</h3></th>
            </tr>

            <tr>
                <th>Delayed tasks</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Scheduled tasks</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Email</h3></th>
            </tr>

            <tr>
                <th>Plain text email</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>HTML email</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Static assets</h3></th>
            </tr>

            <tr>
                <th>Addon contributed JS and CSS </th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Extensible widget CSS and JS inclusion on a page</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Cache busting</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Devops</h3></th>
            </tr>

            <tr>
                <th>Deployment model with staging and production</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Colored log output</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Backuping</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th colspan="5"><h3>Testing and debugging</h3></th>
            </tr>
            <tr>
                <th>Debug toolbar</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th>Unit testing</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
            </tr>

            <tr>
                <th>Functional testing - plain response</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="built-in"></td>
                <td class="not-exist"></td>
            </tr>

            <tr>
                <th>Functional testing with JavaScript and CSS</th>
                <td class="built-in"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
                <td class="not-exist"></td>
            </tr>

        </tbody>
    </table>

    <p></p>


    <p id="installed-apps">
        <sup>
            1) Django initialization is driven by framework which reads <code>settings.py</code> file. For a developer it's not very transparent and customizable how and in which order things are set up.
        </sup>
    </p>

    <p id="settings-inclusion">
        <sup>
            2) Django supports including other settings files from <code>settings.py</code>, but the mechanism is not standardized.
        </sup>
    </p>

    <p id="mixin">
        <sup>
            3) <a href="http://programmers.stackexchange.com/q/218458">The overusage of mixin and multiple inheritance may often lead to a "mixin hell"</a>.
        </sup>
    </p>

    <p id="mixin">
        <sup>
            4) Integrated IPython Notebook web shell
        </sup>
    </p>
