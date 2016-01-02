from zope.interface import Interface


class IModel(Interface):
    """Marker the class which declares SQLAlchemy model.

    This marker interface is used e.g. by ModelAdmin for registry mappings between model and ModelAdmin. We cannot implicitly assume everything is inherited from ``.meta.Base`` because there could be plugin models and such.
    """
