=====
Views
=====

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

This is the easiest way to add a view is to use :py:func:`websauna.system.core.route.simple_route` decorator

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

Imperative route and declarative view config
--------------------------------------------

See

* :py:meth:`pyramid.configurator.Configurator.add_view`

* :py:meth:`pyramid.configurator.Configurator.add_route`

Context sensitive views
-----------------------

If you are using :term:`traversal` views take an additional ``context`` argument which is an instance of :py:class:`websauna.system.core.traversal.Resource`. The :term:`router` resolves a view with most accurate context class match, so if you want to override any stock views, subclass them and change context to your own resource class. Websauna provides :py:func:`websauna.viewconfig.view_overrides` decorator which helps here.

Example how to get a custom listing view for the :term:`admin` of ``Review`` model.

``admin.py``::

    from websauna.system import admin

    # We implement a subclass of ModelAdmin with a subclass for a resource
    @admin.ModelAdmin.register(model='myapp.models.Review')
    class Review(admin.ModelAdmin):
        class Resource(admin.ModelAdmin.Resource):
            pass

Below is a corresponding view example. :py:func:`websauna.viewconfig.view_overrides` sets a context for ``ReviewListing.listing()`` (implemented in :py:func:`websauna.system.crud.views.Listing.listing`) to a Review.Resource class. Because Review.Resource is more accurate than its parent :py:class:`websauna.system.admin.ModelAdmin.Resource` this view gets picked up instead of the stock admin listing.

``adminviews.py``::


    from websauna.viewconfig import view_overrides
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