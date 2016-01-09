==========================
Notebook and IPython shell
==========================

.. _notebook:

Websauna comes with an integrated `IPython Notebook <http://ipython.org/notebook.html>`_ shell. When it's enabled you can directly open IPython Notebook shell from your website with a single click. It also serves as more user friendly alternative for terminal based shell.

.. image:: ../../tutorial/images/notebook.png
    :width: 640pxc

Enabling Notebook
=================

Notebook shell is very powerful, equal to giving a full shell access to a person. Thus it is disabled by default. You need to enable notebook for each user by whitelisting username or email in your application configuration file.

* :ref:`development.ini` allows notebook access for admin uses

* :ref:`production.ini` needs to whitelist all users with notebook access individually

For more information see :ref:`websauna.superusers` and :ref:`websauna.admin_as_superuser` settings.

Opening context sensitive notebook
==================================

You can open a notebook in any part of your site and prepopulate it with data. An example of this is the default admin interface which can open shell for any shown item.

How to do this see :py:func:`websauna.system.notebook.views.launch_context_sensitive_shell` and :py:class:`websauna.system.admin.views.Shell`.

Limitations
===========

The notebook process is spawned separately from the web server. Each user can hold only one active notebook session. The notebook process automatically terminated 30 minutes after the launch unless the user shuts it down.

Currently IPython Notebook feature works with localhost and certain production web servers only. Refer to :term:`pyramid_notebook` for more information.
