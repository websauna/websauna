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

The modern web development is not simple having a script on the server which writes HTTP response on HTTP request read. The topics cover tasks liek setting up servers, optimizing response times, balancing the load, handling operations securely. Websauna does not force its approaches upon the developers, but offers at least one solution to tackle each of the issues required for the full website life cycle management.

Frameworks
==========

Websauna
--------

A working website with sign in and sign up out of the box. Build the first version fast, but make sure the developer is on a driver's seat for iteratively scale up and replace components and parts of the stack.

Pyramid
-------

A small, fast, down-to-earth, open source.

Django
------

Python Web framework that encourages rapid development and clean, pragmatic design.

Flash
-----

Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions.

Comparison
==========

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

    <p class="built-in">Built-in: The framework supports this out of the box</p>
    <!--
    <p>Configurable: The framework supports this out of the box, but does not provide default configuration</p>
    -->
    <p class="addon">addon: There is a known third party package with moderate setup cost for this subsystem</p>
    <p class="integration-needed">Integration needed: moderate to advanced integration work is needed to enable this feature</p>
    <p class="unopionated">Unopionated or not there: the framework does not suggest a choice for this</p>
    <p class="no-data">No data: No information available - please add</p>

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
                <th>Barries included approach</th>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>SQL modelling</th>
                <td class="built-in"></td>
                <td class="not-there"></td>
                <td class="built-in"></td>
                <td class="not-there"></td>
            </tr>

            <tr>
                <th>Global variable free</th>
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
                <th>Access control lists and permission hierarchy</th>
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
                <th>Addon mechanism</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="no-data"></td>
            </tr>

        </tbody>
    </table>


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
