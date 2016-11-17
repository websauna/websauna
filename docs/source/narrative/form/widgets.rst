=======
Widgets
=======

.. contents:: :local:

Introduction
============

Websauna comes with special :term:`Deform` form widget support, mainly to deal with SQLAlchemy models. For complete Deform built-in widget reference see `Deform demo site <http://deformdemo.repoze.org/>`_.

.. _sqlalchemy-widgets:

SQLAlchemy widgets
==================

Choose one instance
-------------------

Use :py:class:`websauna.system.form.sqlalchemy.ForeignKeyValue` and :py:class:`websauna.system.form.sqlalchemy.UUIDForeignKeyValue`.

An example below. :py:func:`websauna.system.form.fields.defer_widget_values` is used to lazily populate value list during the run-time.

.. code-block:: python

    import colander
    import deform
    import deform.widget
    from websauna.system.form.schema import CSRFSchema
    from websauna.utils.slug import uuid_to_slug
    from websauna.system.form.sqlalchemy import UUIDForeignKeyValue
    from websauna.system.form.fields import defer_widget_values


    def available_networks(node: colander.SchemaNode, kw: dict) -> list:
        """Create """
        request = kw["request"]
        query = request.dbsession.query(AssetNetwork).all()
        return [(uuid_to_slug(network.id), network.name) for network in query]


    class MoveNetworkSchema(CSRFSchema):

        #: Choose network there this item belongs to
        network = colander.SchemaNode(
            UUIDForeignKeyValue(model=AssetNetwork, match_column="id"),
            widget=defer_widget_values(deform.widget.SelectWidget, available_networks),
        )


    # Ten some example view

    @view_config(context=AssetDescription, route_name="network", name="move", permission="manage-content", renderer="network/rename.html")
    def move(asset_desc: AssetDescription, request: Request):
        """Rename asset.

        Allow change it title and symbol, but optionally keep slug intact.
        """

        schema = MoveNetworkSchema().bind(request=request)
        asset = asset_desc.asset  # type: websauna.wallet.models.Asset

        # ...

        # User submitted this form
        if request.method == "POST":

            try:
                appstruct = form.validate(request.POST.items())

                # We get direct SQLAlchemy reference here
                asset.network = appstruct["network"]

            except deform.ValidationFailure as e:
                # Render a form version where errors are visible next to the fields,
                # and the submitted values are posted back
                rendered_form = e.render()
        else:

            # Populate default values
            appstruct = {
                "network": asset.network,
            }
            # Render a form with initial values
            rendered_form = form.render(appstruct=appstruct)

        return locals()


Choose multiple instances
-------------------------

TODO

See :py:mod:`websauna.system.form.sqlalchemy`.

Other widgets
=============

See :py:mod:`websauna.system.form.widgets` and :py:mod:`websauna.system.form.fields`.





