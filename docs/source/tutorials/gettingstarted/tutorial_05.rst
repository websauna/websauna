========================
Local development server
========================

Local development server is a web server running on your computer when you edit your application source code. It reflects changes in Python and template files instantly. :term:`Pyramid` web framework provides :ref:`ws-pserve` command for this.

Starting a local web development server
---------------------------------------

Run::

    ws-pserve ws://company/application/conf/development.ini --reload

The web server keeps running until

* It fails to reload due to syntax error in edited code

* You terminate it with CTRL + C

If this command gives you ``SanityCheckError`` about **Redis** or **PostgreSQL** make sure :ref:`you a running Redis server on your computer <installing_websauna>`.

Checking your site for the first time
-------------------------------------

Point your web browser to `http://localhost:6543 <http://localhost:6543>`_.

.. image:: images/welcome.png
    :width: 640px

Creating your admin user
------------------------

.. note::

    This method highlights creating the initial site administrator user from the command line, using email and password. You can also configure any of social media logins (Facebook, Google) as described later in this tutorial. If your first login to the site comes through social media accounts, the very first logged in user becomes admin.

On a shell where your projects virtual environment is activated, cd into ``myproject/company.application`` and type::

    ws-create-user company/application/conf/development.ini myemail@example.com

This will prompt you for a password for the new user. Because this is the first user of the site, the user becomes an administrator.

Now you can log in as this user and you should see the site administration.

.. image:: images/login.png
    :width: 640px

Exploring admin interface
-------------------------

Click *Admin* in the top navigation bar and you can access the administration interface. This is, where all newly created models will become visible. More about this later.

.. image:: images/admin.png
    :width: 640px
