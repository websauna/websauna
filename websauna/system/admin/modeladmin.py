"""Automatic admin and CRUD for SQLAlchemy models."""

import venusian
import zope
from pyramid.interfaces import IRequest
from websauna.system.admin.interfaces import IModelAdmin, IModel
from websauna.system.compat import typing
from websauna.system.core.traverse import Resource
from websauna.system.crud.sqlalchemy import CRUD as CRUD
from websauna.system.crud.sqlalchemy import Resource as AlchemyResource
from zope.interface import classProvides


class ModelAdmin(CRUD):
    """Resource presenting one model in admin interface.

    Provide automatized list, show add, edit and delete actions for an SQLAlchemy model which declares admin interface.
    """

    #: Title used in breadcrumbs, other places
    title = None

    #: Model must be set by subclass
    model = None

    def __init__(self, request):
        import pdb ; pdb.set_trace()
        assert self.model, "Model must be set by a subclass"
        super(ModelAdmin, self).__init__(request)

    #: Our resource factory
    class Resource(AlchemyResource):
        pass

    def get_admin(self):
        """Get Admin resource object."""
        return self.__parent__.__parent__

    def get_title(self):
        if self.title:
            return self.title
        return self.id.capitalize()


class ModelAdminRoot(Resource):
    """Admin resource under which all model admins lurk."""

    def get_model_admins(self):
        """List all registered model admin classes.

        :yield: (model_id, IModelAdmin) tuples
        """

        for model_id, model_cls in self.request.registry.getAdapters([self.request], IModelAdmin):
            yield(model_id, model_cls)

    def __getitem__(self, item):

        registry = self.request.registry
        model_admin_resource = registry.queryAdapter([self.request], IModelAdmin, name=item)
        import pdb ; pdb.set_trace()
        if not model_admin_resource:
            raise RuntimeError("Did not find model admin with id: {}".format(item))

        Resource.make_lineage(self, model_admin_resource, item)
        return model_admin_resource

    def items(self) -> typing.List[typing.Tuple[str, ModelAdmin]]:
        for id in self.get_model_admins():
            yield id, self[id]


def model_admin(traverse_id:str):
    """Class decorator to mark the class to become part of model admins.

    ``Configure.scan()`` must be run on this module for the definitino to be picked up.

    :param traverse_id: Under which URL id this model appears in the admin interface

    :param model_cls: Which model class this admin resource is controlling
    """
    def _inner(cls):
        "The class decorator example"

        def register(scanner, name, wrapped):
            config = scanner.config
            config.registry.registerAdapter(cls, required=[IRequest], provided=IModelAdmin, name=traverse_id)


        classProvides(cls, IModelAdmin)

        venusian.attach(cls, register, category='websauna')
        return cls

    return _inner