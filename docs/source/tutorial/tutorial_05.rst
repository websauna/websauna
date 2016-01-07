========================
Local development server
========================

Local development server is a web server running on your computer when you edit your application source code. It reflects changes in Python and template files back instantly. :term:`Pyramid` web framework provides :term:`pserve` command for this.

Starting a local web development server
---------------------------------------

Run::

    pserve development.ini --reload

The web server keeps running until

* It fails to reload due to syntax error in edited code

* You terminate it with CTRL + C

Checking your site for the first time
-------------------------------------

Point your web browser to `http://localhost:6543 <http://localhost:6543>`_.

Creating your admin user
------------------------

.. note ::

    This method highlights creating the initial site administrator user from the command line, using email and password. You can also configure any of social media logins (Facebook, Google) as described later in this tutorial. If your first login to the site comes through social media accounts the firstly logged in user becomes admin.

On a terminal type::

    ws-create-user myemail@example.com secret

This will create a new user. Because this is the first user of the site the user becomes an administrator.

Now you can log in as this user and you should see the site administration.