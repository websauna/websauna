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

The first user who logs into to the site will become the site administrator. Below is an example how you can do it with email sign up. If you wish to use federated authentication (Facebook, Google) you can set it up as instructed in this tutorial later on.

To sign up on your local site

* Open your development site

* Go to sign up link

* Sign up with your email address.

* There is no actual outgoing activation email. Websauna development site (:term:`development.ini`) has been configured to write outgoing emails to your terminal, instead of sending out actual emails. Look your terminal and find the activation link.

Example piece of printed email with activation link highlighted:



