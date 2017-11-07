===================
Git version control
===================

Introduction
============

``websauna.ansible`` playbook is designed to deploy the Websauna Python application from a remote Git repository.

* Push your Websauna application Python package to a Git repository

* Playbook will later use :term:`ssh agent` and your credentials to clone this repository on the deployment server

* By default the playbook deploys from a ``master`` branch, but this is configurable

Git hosting
===========

If you are not using Git hosting yet there two are the most popular options

* `Bitbucket <https://bitbucket.org>`_: limited number of free private repositories

* `GitHub <https://github.com>`_: free for open source repositories