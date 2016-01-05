==========================
Notebook and IPython shell
==========================

Websauna comes with an integrated `IPython Notebook <http://ipython.org/notebook.html>`_ shell. When it's enabled you can directly open IPython Notebook shell from your website with a single click. It also serves as more user friendly alternative for terminal based shell.

Enabling Notebook
=================

Notebook shell is very powerful, equal to giving a full shell access to a person. Thus it is disabled by default. You need to enable notebook for each user by whitelisting username or email in your application configuration file.

Edit ``development.ini`` and add in ``[main]`` section a list of whitelisted user email addresses. Usually this is the email address you used to sign up to the site initially::

    websauna.superusers =
        example@example.com

Limitations
===========

Currently IPython Notebook feature works with localhost and certain production stite web servers only. Refer to `pyramid_notebook README <https://bitbucket.org/miohtama/pyramid_notebook>`_ for more information.
