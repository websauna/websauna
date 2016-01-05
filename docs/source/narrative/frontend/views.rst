=====
Views
=====

Introduction
============

The main component of Websauna is *views*. Usually view is

* Mapped to a certain URL path on your site e.g. ``/profile``

* Is pair or Python function or class and template

* May have permission requirements set on it

Configuring views
=================

Imperative route and declarative view config
--------------------------------------------

Imperative route and imperative view config
-------------------------------------------


Simple route + view
-------------------

Class-based views
-----------------

Context sensitive views
-----------------------


Requiring login
---------------

To make sure the user is logged in when accessing the view use pseudopermission ``authenticated``. Example::

    @simple_route("/affiliate", route_name="affiliate", renderer="views/affiliate.html", append_slash=False, permission="authenticated")
    def affiliate_program(request):