.. _views:

=====
Views
=====

.. contents:: :local:

Introduction
============

The main component of Websauna is :term:`view`. Usually a view is

* Mapped to a certain URL path on your site e.g. ``/profile``

* Is a Python function or class

* Have a template associated with it, through a ``renderer``

* May have permission requirements set on it

For more information please read the `Views chapter in Pyramid documentation <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html>`_. Also see Getting started tutorial.

Configuring views
=================

Simple route
------------

The easiest way to add a view is to use :py:func:`websauna.system.core.route.simple_route` decorator.

Add to ``views.py`` or any other module in your application::

    @simple_route("/", route_name="home", renderer="myapp/home.html")
    def home(request: Request):
        """Render the site homepage."""
        latest_question_list = request.dbsession.query(Question).order_by(Question.published_at.desc()).all()[:5]
        return locals()

To make ``simple_route`` decorator effective, you must scan the Python module in the :term:`Initializer` or your app::

    import websauna.system

    class Initializer(websauna.system.Initializer):

        def configure_views(self):
            from . import views
            self.config.scan(views)

For more information see

* :py:func:`websauna.system.core.route.simple_route`

Imperative route and view config
--------------------------------

See

* :py:meth:`pyramid.configurator.Configurator.add_view`

* :py:meth:`pyramid.configurator.Configurator.add_route`

Examples

* :py:meth:`websauna.system.Initializer.configure_notebook`

Context sensitive views
-----------------------

If you are using :term:`traversal` views take an additional ``context`` argument which is an instance of :py:class:`websauna.system.core.traversal.Resource`. The :term:`router` resolves a view with most accurate context class match, so if you want to override any stock views, subclass them and change context to your own resource class. Websauna provides :py:func:`websauna.system.core.viewconfig.view_overrides` decorator which helps here.

Example how to get a custom listing view for the :term:`admin` of ``Review`` model.

``admin.py``::

    from websauna.system import admin

    # We implement a subclass of ModelAdmin with a subclass for a resource
    @admin.ModelAdmin.register(model='myapp.models.Review')
    class Review(admin.ModelAdmin):
        class Resource(admin.ModelAdmin.Resource):
            pass

Below is a corresponding view example. :py:func:`websauna.system.core.viewconfig.view_overrides` sets a context for ``ReviewListing.listing()`` (implemented in :py:func:`websauna.system.crud.views.Listing.listing`) to a Review.Resource class. Because Review.Resource is more accurate than its parent :py:class:`websauna.system.admin.ModelAdmin.Resource` this view gets picked up instead of the stock admin listing.

``adminviews.py``::


    from websauna.system.core.viewconfig import view_overrides
    from websauna.system.admin import views as adminviews
    from websauna.system.crud import listing

    from . import admin

    # view_overrides sets context parameter form ReviewListing.

    @view_overrides(context=admin.Review)
    class ReviewListing(adminviews.Listing):

        title = "All reviews"

        table = listing.Table(
            columns = [
                listing.Column("id", "Id",),
                listing.Column("delivery_id", "Delivery", navigate_url_getter=get_delivery_link_from_review),
                listing.Column("customer", "Customer", getter=lambda obj: obj.customer.friendly_name, navigate_url_getter=get_customer_link_from_review),
                listing.Column("product", "Product"),
                listing.FriendlyTimeColumn("completed_at", "Completed at", timezone="US/Pacific"),
                listing.Column("rating", "Rating"),
                listing.Column("comment", "Comment"),
            ]
        )

Protecting views with permissions
---------------------------------

To make sure the user is logged in when accessing the view use pseudopermission ``authenticated``. Example::

    @simple_route("/affiliate", route_name="affiliate", renderer="views/affiliate.html", append_slash=False, permission="authenticated")
    def affiliate_program(request):

Doing redirects
===============

Below is an example how to do a redirect (HTTP 302 temporary redirect) for logged in users using :py:class:`pyramid.httpexceptions.HTTPFound`:

.. code-block:: python

    from pyramid.httpexceptions import HTTPFound
    from websauna.system.http import Request
    from websauna.system.core.route import simple_route


    @simple_route("/", route_name="home", renderer='myapp/home.html')
    def home(request: Request):
        """Render site homepage."""

        if request.user:
            # Logged in users go directly from home to profile page
            return HTTPFound(request.route_url("profile"))

        return {"project": "My App"}


    @simple_route("/profile", route_name="profile", renderer='myapp/profile.html')
    def profile(request: Request):
        return {}


.. note::

    One could also do a redirect by ``raise HTTPFound()`` and let exception handling mechanism to perform the redirect. In this case, however, nothing is written to the database, like user login records, because exceptions cause transaction rollback.

Class based views
=================

Views can be also class based, allowing one to easily recycle methods across view logic.

Example ``backoffice.views.api`` module that you can scan in ``configure_views()`` using ``config.scan()``:

.. code-block:: python

    import binascii

    from pyramid.view import view_defaults
    from websauna.system.core.route import simple_route

    from ..models import CardEventSourceType
    from ..card import provision
    from ..card import get_ownership_info


    @view_defaults(renderer='json', require_csrf=False)  # Set defaults for all API calls
    class APIView:
        """Base class for API renderers."""

        def __init__(self, request):
            self.request = request

        def get_agent(self):
            return None

        def get_event_source(self):
            return CardEventSourceType.simulation


    class Provision(APIView):
        """"NFC card provisioning API endpoint."""

        @simple_route("/api/provision", route_name="api_provision")
        def provision(self):
            """Provision a new card."""

            request = self.request
            agent = self.get_agent()
            event_source = self.get_event_source()

            box_no = request.params["box_serial_number"]
            card_no = binascii.unhexlify(request.params["card_serial_number"])

            box, card = provision(request.dbsession, box_no, card_no, event_source, agent=agent)

            ownership_info = get_ownership_info(box)

            return {"status": "ok", "ownership_info": ownership_info}



Stock views
===========

Some special views Websauna provides out of the box.

Home
----

Websauna application scaffold provides a route with name ``home``. This should point to the landing page of your website.

This view is referred e.g. sign up emails.

Example

.. code-block:: html+jinja

        <h2>
          <a href="{{ 'home'|route_url }}">
            <img class="logo" src="{{ 'myapp:static/logo.png'|static_url }}" alt="{{ site_name }}">
          </a>
        </h2>

HTTP 404 Not Found
------------------

Configured in :py:meth:`websauna.system.Initializer.configure_error_views`. Implemented in :py:meth:`websauna.system.core.notfound`.


HTTP 403 Forbidden
------------------

Configured in :py:meth:`websauna.system.Initializer.configure_error_views`. Implemented in :py:mod:`websauna.system.core.forbidden`.


HTTP 500 internal server error
------------------------------

Configured in :py:meth:`websauna.system.Initializer.configure_error_views`. Implemented in :py:mod:`websauna.system.core.internalservererror`.

Error test view
---------------

This is a test view which raises a runtime error if you access it through ``/error-trigger``.

Configured in :py:meth:`websauna.system.Initializer.configure_error_views`. Implemented in :py:mod:`websauna.system.core.errortrigger`.

Shorthand redirect
==================

You can add quick redirects in Python modules with :py:func:`websauna.system.core.redirect.redirect_view`.
