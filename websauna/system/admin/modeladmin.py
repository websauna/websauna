"""Automatic admin and CRUD for SQLAlchemy models."""

import venusian
from pyramid.interfaces import IRequest
from websauna.system.admin.interfaces import IModelAdmin, IModel
from websauna.system.core.traverse import Resource
from websauna.system.crud.sqlalchemy import CRUD as CRUD
from websauna.system.crud.sqlalchemy import Resource as AlchemyResource


class ModelAdmin(CRUD):
    """Resource presenting one model in admin interface.

    Provide automatized list, show add, edit and delete actions for an SQLAlchemy model which declares admin interface.
    """

    #: Title used in breadcrumbs, other places
    title = None

    #: Our resource factory
    class Resource(AlchemyResource):
        pass

    def get_model(self) -> type:
        """Return the model for which this admin is registered for."""
        registry = self.request.registry
        return registry.getAdapter([self], IModel)

    def get_admin(self):
        """Get Admin resource object."""
        return self.__parent__.__parent__

    def get_title(self):
        if self.title:
            return self.title
        return self.id.capitalize()


class ModelAdminRoot(Resource):
    """Admin resource under which all model admins lurk."""

    def get_models(self):
        """List all registered models.

        :yield: (id, class) tuples
        """

        for a in self.request.registry.getAdapters([self.request], IModelAdmin):
            yield(a[0], a[1])

    def __getitem__(self, item):

        registry = self.request.registry
        model = registry.queryAdapter(self.request, IModel, name=item)
        import pdb ; pdb.set_trace()
        model_admin_resource = self.request.registry.queryAdapter([self.request, model], IModelAdmin, name=item)
        import pdb ; pdb.set_trace()
        if not model_admin_resource:
            raise RuntimeError("Did not find model admin with id: {}".format(item))

        Resource.make_lineage(self, model_admin_resource, item)
        return model_admin_resource

    def items(self):
        for id in self.get_models():
            yield id, self[id]


def model_admin(traverse_id:str, model:type):
    """Class decorator to mark the class to become part of model admins.

    ``Configure.scan()`` must be run on this module for the definitino to be picked up.

    :param traverse_id: Under which URL id this model appears in the admin interface

    :param model_cls: Which model class this admin resource is controlling
    """
    def _inner(cls):
        "The class decorator example"

        def register(scanner, name, wrapped):
            config = scanner.config
            config.registry.registerAdapter(model, required=[IRequest], provided=IModel, name=traverse_id)
            config.registry.registerAdapter(cls, required=[IRequest, IModel], provided=IModelAdmin, name=traverse_id)
            #config.registry.registerAdapter(model, required=[IRequest], provided=IModel, name=traverse_id)
            #config.registry.registerAdapter(cls, required=[IRequest], provided=IModelAdmin, name=traverse_id)

        venusian.attach(cls, register, category='websauna')
        return cls

    return _inner