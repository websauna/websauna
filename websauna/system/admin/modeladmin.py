"""Automatic admin and CRUD for SQLAlchemy models."""
import sys

from pyramid.events import subscriber

from websauna.system.admin import AdminConstruction
from websauna.system.admin import menu
from websauna.system.admin.interfaces import IModelAdminRegistry
from websauna.system.core.traverse import Resource
from websauna.system.crud.sqlalchemy import CRUD as CRUD
from websauna.system.crud.sqlalchemy import Resource as AlchemyResource
from zope.interface import implements


class ModelAdmin(CRUD):
    """Present one model in admin interface.

    Provide automatized list, show add, edit and delete actions for an SQLAlchemy model which declares admin interface.
    """

    #: Title used in breadcrumbs, other places
    title = None

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


@implements(IModelAdminRegistry)
class ModelAdminRegistry:
    """Hold a registry of model admins."""

    # Hold references to the scanned model admins
    model_admins = {}

    @classmethod
    def register(cls, model):
        """Mark the class to become a model admin on Admin.scan()."""

        def inner(wrapped_cls):

            assert cls.__module__, "Class without module attached cannot possibly work"

            # XXX: Now store registered model admins in a module attribute, which will be later picked up scan(). Think some smarter way to do this, like using events and pyramid config registry.
            module = sys.modules[wrapped_cls.__module__]
            __admin__ = getattr(module, "__admin__", {})
            __admin__[model] = wrapped_cls
            module.__admin__ = __admin__

            return wrapped_cls

        return inner

    @classmethod
    def scan(cls, config, module):
        """Picks up admin definitions from the module.

        TODO: This is poor-man's Venusian replacement until we get proper implementation.
        """

        __admin__ = getattr(module, "__admin__", None)

        if not __admin__:
            raise RuntimeError("Admin tried to scan module {}, but it doesn't have __admin__ attribute. The module probably doesn't define any admin objects.".format(module))

        for model_dotted, admin_cls in __admin__.items():

            # Instiate model admin
            try:
                model_cls = config.maybe_dotted(model_dotted)
            except ImportError as e:
                raise ImportError("Tried to initialize model admin for {}, but could not import it".format(model_dotted)) from e

            id = getattr(model_cls, "id", None)
            if not id:
                raise RuntimeError("Model admin does not define id {}".format(model_cls))

            cls.model_admins[id] = model_cls

    def get_admin_resource(self, obj):
        """Get a admin traversable item for a SQLAlchemy object.

        To get admin URL of an SQLAlchemy object::

        :param obj: SQLAlchemy model instance
        """
        assert obj is not None, "get_admin_resource() you gave me None, I give you nothing"

        model = obj.__class__
        model_admin = self.get_admin_for_model(model)

        path = model_admin.mapper.get_path_from_object(obj)
        return model_admin[path]


class ModelAdminRoot(Resource):
    """Admin resource under which all model admins lurk."""

    def __getitem__(self, item):
        model_admin_registry = self.request.registry.getUtility(IModelAdmin)
        model_admin_class = model_admin_registry[item]
        model_admin_resource = model_admin_class(self.request)
        make_lineage(self, model_admin_resource, item)
        return model_admin_resource


@subscriber(AdminConstruction)
def contribute_admin(event):
    """Add model menus to the admin user interface."""
    admin = event.admin

    admin.chilren["models"] = ModelAdminRoot(admin.request)

    # Create a model listing entry
    data_menu = admin.get_admin_menu().get_entry("admin-menu-data").submenu
    entry = menu.TraverseEntry("admin-menu-data-{}".format(id), label=model_admin.title, context=model_admin, name="listing")
    data_menu.add_entry(entry)




