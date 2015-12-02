from websauna.system.admin.interfaces import IAdmin
from websauna.system.core.traverse import Resource


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


