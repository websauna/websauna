from websauna.system.admin.interfaces import IAdmin
from websauna.system.core.traverse import Resource
from websauna.system.model.meta import Base


def get_admin(request) -> IAdmin:
    """Get hold of admin singleton."""
    admin_class = request.registry.queryUtility(IAdmin)
    return admin_class(request)


def get_admin_for_model(admin:IAdmin, model:type) -> Resource:
    """Return Admin resource for a model manager interface."""

    model_manager = admin["models"]

    if not model.id in model_manager:
        raise KeyError("No admin defined for model: {}".format(model))
    return model_manager[model.id]


def get_model_admin_for_sqlalchemy_object(admin:IAdmin, instance:type) -> Resource:
    """Return Admin resource for a SQLAlchemy object instance.

    :param admin: Admin root object

    :param instance: SQLAlchemy object
    """

    model_manager = admin["models"]

    registry = admin.request.registry
    model = instance.__class__

    model_admin_id = registry.model_admin_ids_by_model.get(model)
    assert model_admin_id, "No ModelAdmin configured for model {}".format(model)

    return model_manager[model_admin_id]


def get_admin_url_for_sqlalchemy_object(admin:IAdmin, instance:type) -> str:
    """Return direct URL to the admin view page of this objet.

    :param admin: Admin root object

    :param instance: SQLAlchemy object
    """
    model_admin = get_model_admin_for_sqlalchemy_object(admin, instance)
    return model_admin.get_object_url(instance)

