========================
Local development server
========================

Local development server is a web server running on your computer when you edit your application source code. It reflects changes in Python and template files back instantly. :term:`Pyramid` web framework provides :term:`pserve` command for this.

Starting a local web development server
---------------------------------------

Run::

    pserve development.ini --reload

Checking your site for the first time
-------------------------------------

Point your web browser to `http://localhost:6543 <http://localhost:6543>`_.

Logging in as admin
-------------------

The first user who logs into to the site will become the site administrator.

To sign up on your local site

* Go to sign up

* Sign up with ``yourname@example.com`` email. ``example.com`` domain is purposefully reserved for non-functional email addresses.

* There is no outgoing activation email. Websauna development site (:term:`development.ini`) has been configured to write out emails to your terminal, instead of sending out them.

