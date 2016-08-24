======================================
Comparing Websauna to other frameworks
======================================

.. warning::

    This page is not up-to-date and is being rewritten.

Below is a comparison with Websauna and other popular Python frameworks.

Websauna does not want to offer only a pile of Python code for the developers to play with - it wants to offer enough tools and integrated approach to cover the full website lifecycle.

Websauna does things differently as it...

* wants to offer a functional site out of the box

* does not make too tight couping between the components, like CRUD and models

* standardizes timed and asynchronous tasks

* extends framework to cover basic devops like backups

The modern web development is not simple having a script on the server which writes HTTP response on HTTP request read. The topics cover tasks like setting up servers, optimizing response times, balancing the load, handling operations securely. Websauna does not force its approaches upon the developers, but offers at least one solution to tackle each of the issues required for the full website life cycle management.

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

        .unopionated {
            background: #eee;
        }

        .no-data {
            background: #aaf;
        }

        .comparison td,
        .comparison th {
            vertical-align: top;
        }
    </style>

    <p class="built-in">Built-in: The framework supports this out of the box</p>
    <!--
    <p>Configurable: The framework supports this out of the box, but does not provide default configuration</p>
    -->
    <p class="addon">addon: There is a known third party package with moderate setup cost for this subsystem</p>
    <p class="integration-needed">Integration needed: moderate to advanced integration work is needed to enable this feature</p>
    <p class="unopionated">Unopionated: the framework does not suggest a choice for this</p>
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
                <th colspan="4"><h3>Philosophy and design</h3></th>
            </tr>

            <tr>
                <th>Pitch</th>
                <td class="built-in">A working site with login and sign up out of the box</td>
                <td class="built-in">A small, fast, down-to-earth, open source</td>
                <td class="built-in">Python Web framework that encourages rapid development and clean, pragmatic design.</td>
                <td class="built-in">Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions.</td>
            </tr>

            <tr>
                <th>Usage of global and thread local variables</th>
                <td class="built-in">No globals</td>
                <td class="built-in">No globals</td>
                <td class="built-in">settings.py constants</td>
                <td class="built-in">heavily embraced</td>
            </tr>

            <tr>
                <th>Traversal</th>
                <td class="built-in"></td>
                <td class="built-in"></td>
                <td class="integration-needed">Not supported</td>
                <td class="integration-needed">Not supported</td>
            </tr>

            <tr>
                <th colspan="4"><h3>Configuration</h3></th>
            </tr>

            <tr>
                <th>Application initialization</th>
                <td class="built-in">Linear, you ramp up application</td>
                <td class="built-in">Linear, you ramp up application</td>
                <td class="built-in">INSTALLED_APPS setting</td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th>Settings</th>
                <td class="built-in">INI files (subject to change)</td>
                <td class="built-in">INI files</td>
                <td class="built-in">settings.py Python based</td>
                <td class="built-in">Python dictionary based</td>
            </tr>

            <tr>
                <th>Extensible config files</th>
                <td class="built-in">INI include hacks</td>
                <td class="integration-needed"></td>
                <td class="built-in">settings.py imports</td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Addon mechanism</th>
                <td class="built-in">Python packages and expanding initialization</td>
                <td class="built-in">Python packages and expanding initialization</td>
                <td class="built-in">INSTALLED_APPS and various hooks</td>
                <td class="no-data"></td>
            </tr>


            <tr>
                <th colspan="4"><h3>HTTP request and response</h3></th>
            </tr>

            <tr>
                <th>HTTP request library</th>
                <td class="built-in">WebOb</td>
                <td class="built-in">WebOb</td>
                <td class="built-in">Django</td>
                <td class="built-in">Werkzeug</td>
            </tr>

            <tr>
                <th>Middleware</th>
                <td class="built-in">Pyramid tweens and WSGI middleware</td>
                <td class="built-in">Pyramid tweens and WSGI middleware</td>
                <td class="built-in">Django middleware</td>
                <td class="built-in">WSGI</td>
            </tr>


            <tr>
                <th colspan="4"><h3>Templates</h3></th>
            </tr>

            <tr>
                <th>Template engine</th>
                <td class="built-in">Jinja 2 and all Pyramid compatible engines</td>
                <td class="unopionated"></td>
                <td class="built-in">Django templates</td>
                <td class="built-in">Jinja 2</td>
            </tr>

            <tr>
                <th>Default site</th>
                <td class="built-in">Bootstrap 3 templates</td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Database and modeling</h3></th>
            </tr>

            <tr>
                <th>Models</th>
                <td class="built-in">SQLAlchemy</td>
                <td class="unopionated"></td>
                <td class="built-in">Django ORM</td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>NoSQL and schemaless data support</th>
                <td class="built-in">PostgreSQL JSONB</td>
                <td class="unopionated"></td>
                <td class="addon">django-nonrel</td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Migrations</th>
                <td class="built-in">Alembic</td>
                <td class="unopionated"></td>
                <td class="built-in">Django migrations</td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Third party package migration support</th>
                <td class="built-in">Customized Alembic</td>
                <td class="unopionated"></td>
                <td class="built-in">Django migrations</td>
                <td class="unopionated"></td>
            </tr>


            <tr>
                <th>Session storage</th>
                <td class="built-in">pyramid_redis</td>
                <td class="unopionated"></td>
                <td class="built-in">Django sessions</td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Forms and CRUD</h3></th>
            </tr>

            <tr>
                <th>Form subsystem</th>
                <td class="built-in">Colander and Deform</td>
                <td class="unopionated"></td>
                <td class="built-in">Django forms</td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Form theming</th>
                <td class="built-in">Bootstrap</td>
                <td class="unopionated"></td>
                <td class="integration-needed">Plain HTML</td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th>CRUD</th>
                <td class="built-in">Colander and Deform</td>
                <td class="built-in">Django forms</td>
                <td class="unopionated"></td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Admin interface</h3></th>
            </tr>

            <tr>
                <th>Model admin</th>
                <td class="built-in">CRUD and traversing based, flexible</td>
                <td class="unopionated"></td>
                <td class="built-in">Tighly coupled with SQL</td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Log in and sign up</h3></th>
            </tr>

            <tr>
                <th>Authentication</th>
                <td class="built-in">Pyramid authentication backends</td>
                <td class="built-in">Django authentication backends</td>
                <td class="unopionated"></td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Permissions</th>
                <td class="built-in">Pyramid authorization</td>
                <td class="built-in">Django users and groups</td>
                <td class="unopionated"></td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Default user implementation</th>
                <td class="built-in">Horus: users, groups</td>
                <td class="built-in">Users, groups</td>
                <td class="unopionated"></td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Social login</th>
                <td class="built-in">Authomatic</td>
                <td class="integration-needed"></td>
                <td class="unopionated"></td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Log in and sign up flow</th>
                <td class="built-in"></td>
                <td class="unopionated"></td>
                <td class="addon">django-registration</td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Security</h3></th>
            </tr>

            <tr>
                <th>CSRF tokens</th>
                <td class="built-in"></td>
                <td class="integration-needed"></td>
                <td class="built-in"></td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th>Non-guessable URL IDs</th>
                <td class="built-in">UUID and base64 slugs</td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th>Password encryption</th>
                <td class="no-data"></td>
                <td class="no-data"></td>
                <td class="no-data"></td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th>User audit log</th>
                <td class="no-data"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Site functionality</h3></th>
            </tr>

            <tr>
                <th>Google sitemaps</th>
                <td class="built-in"></td>
                <td class="unopionated"></td>
                <td class="built-in"></td>
                <td class="unopionated"></td>
            </tr>

            <tr>
                <th>Session messages</th>
                <td class="built-in"></td>
                <td class="unopionated"></td>
                <td class="built-in"></td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Email</h3></th>
            </tr>

            <tr>
                <th>Plain text email</th>
                <td class="built-in">pyramid_mailer integrated</td>
                <td class="addon">pyramid_mailer available</td>
                <td class="built-in"></td>
                <td class="addon">flask-mail</td>
            </tr>

            <tr>
                <th>Rich text HTML email</th>
                <td class="built-in">premailer integrated</td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th>Email and transaction integration</th>
                <td class="built-in"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Static assets</h3></th>
            </tr>

            <tr>
                <th>Cache busting</th>
                <td class="built-in">Pyramid cachebusting</td>
                <td class="built-in">Django staticfiles</td>
                <td class="built-in">Pyramid cachebusting</td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Internationalization</h3></th>
            </tr>

            <tr>
                <th>gettext</th>
                <td class="integration-needed">Not available in the current versions</td>
                <td class="built-in">Django i18n and gettext</td>
                <td class="built-in">Pyramid i18n and gettext</td>
                <td class="addon">Flask-Babel</td>
            </tr>

            <tr>
                <th colspan="4"><h3>Timed tasks and asynchronous procesing</h3></th>
            </tr>

            <tr>
                <th>Cron-like functionality</th>
                <td class="built-in">pyramid_celery</td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th>Delayed tasks</th>
                <td class="built-in">pyramid_celery</td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Testing</h3></th>
            </tr>

            <tr>
                <th>Debug toolbar</th>
                <td class="built-in">pyramid_debugtoolbar</td>
                <td class="addon">pyramid_debugtoolbar</td>
                <td class="addon">django-debug-toolbar</td>
                <td class="addon">flask-debugtoolbar</td>
            </tr>

            <tr>
                <th>Unit testing</th>
                <td class="built-in">py.test</td>
                <td class="built-in">unittest</td>
                <td class="built-in">unittest</td>
                <td class="built-in">unittest</td>
            </tr>

            <tr>
                <th>Functional testing (Plain HTML)</th>
                <td class="built-in">Splinter and Selenium</td>
                <td class="addon">WebTest</td>
                <td class="built-in">Django test request</td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th>Functional testing with JavaScript</th>
                <td class="built-in">Splinter and Selenium</td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th colspan="4"><h3>Devops</h3></th>
            </tr>

            <tr>
                <th>Secrets management</th>
                <td class="built-in">Separate secrets.ini (subject to change)</td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th>Colored log output</th>
                <td class="built-in"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th>Backup</th>
                <td class="built-in">Duplicity</td>
                <td class="integration-needed"></td>
                <td class="integration-needed">Various guides</td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th>Deployment</th>
                <td class="no-data"></td>
                <td class="no-data"></td>
                <td class="no-data"></td>
                <td class="no-data"></td>
            </tr>

            <tr>
                <th>Sentry error logging</th>
                <td class="built-in"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>

            <tr>
                <th>New Relic instrumentation</th>
                <td class="built-in"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
                <td class="integration-needed"></td>
            </tr>


        </tbody>
    </table>
