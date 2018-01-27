"""Automatic admin and CRUD for SQLAlchemy models."""
# Standard Library
import string
import typing as t

# Pyramid
import venusian
from pyramid.interfaces import IRequest

# Websauna
from websauna.system.admin.interfaces import IAdmin
from websauna.system.admin.interfaces import IModelAdmin
from websauna.system.core.traversal import Resource
from websauna.system.crud.sqlalchemy import CRUD as CRUD
from websauna.system.crud.sqlalchemy import Resource as AlchemyResource


# We enforce some best practices to readable URL names of model admins. This is an arbitrary choice of the author.
ALLOWED_TRAVERSE_ID_CHARACTERS = string.ascii_lowercase + string.digits + "-"


class ModelAdmin(CRUD):
    """Resource presenting one model in admin interface.

    Provide automatized list, show add, edit and delete actions for an SQLAlchemy model which declares admin interface.
    """

    #: Title used in breadcrumbs, other places
    title = None

    #: Model must be set by subclass
    model = None

    def __init__(self, request):
        super(ModelAdmin, self).__init__(request)

    def get_model(self):
        assert self.model, "Model must be set by a subclass as a class attribute"
        return self.model

    #: Our resource factory
    class Resource(AlchemyResource):

        def get_admin(self):
            return self.__parent__.get_admin()

    def get_admin(self) -> IAdmin:
        """Get Admin resource object."""
        return self.__parent__.__parent__

    def get_title(self) -> str:
        if self.title:
            return self.title
        return self.id.capitalize()


class ModelAdminRoot(Resource):
    """Admin resource under which all model admins lurk.

    To get access this resource:


    """

    def get_title(self):
        return "Models"

    def get_model_admins(self):
        """List all registered model admin classes.

        :yield: (model_id, IModelAdmin) tuples
        """

        for model_id, model_cls in self.request.registry.getAdapters([self.request], IModelAdmin):
            yield(model_id, model_cls)

    def __getitem__(self, item):
        """Traverse to model admins. """
        registry = self.request.registry
        model_admin_resource = registry.queryAdapter(self.request, IModelAdmin, name=item)
        if not model_admin_resource:
            raise RuntimeError("Did not find model admin with id: {}".format(item))

        Resource.make_lineage(self, model_admin_resource, item)
        return model_admin_resource

    def items(self) -> t.List[t.Tuple[str, ModelAdmin]]:
        for id, model_cls in self.get_model_admins():
            yield id, self[id]


def model_admin(traverse_id: str) -> type:
    """Class decorator to mark the class to become part of model admins.

    ``Configure.scan()`` must be run on this module for the implementation to be picked up.

    If there is already an existing model admin with same ``model``, then the existing model admin is overwritten.

    :param traverse_id: Under which URL id this model appears in the admin interface. Allowed to contain lowercase letters, dash and digits. This will be available as ``ModelAdmin.__name__`` instance attribute.

    :param model_cls: Which model class this admin resource is controlling
    """

    assert all(c in ALLOWED_TRAVERSE_ID_CHARACTERS for c in traverse_id), "traverse_id may only contain lowercase letters, digits and a dash: {}".format(traverse_id)

    def _inner(cls):
        "The class decorator example"

        def register(scanner, name, wrapped):
            config = scanner.config
            # We can look up midels by

            model = getattr(cls, "model", None)
            assert model, "Class {} must declare model attribute".format(cls)

            registry = config.registry

            # Purge existing model admin
            registry.unregisterAdapter(required=(IRequest,), provided=IModelAdmin)
            registry.registerAdapter(cls, required=(IRequest,), provided=IModelAdmin, name=traverse_id)
            registry.model_admin_ids_by_model[model] = traverse_id

        venusian.attach(cls, register, category='websauna')
        return cls

    return _inner


def configure_model_admin(config):
    """Sets up model -> model admin registry."""
    config.registry.model_admin_ids_by_model = {}
