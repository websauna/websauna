import sys

from pyramid.security import Allow
from pyramid_web20.system import crud
from pyramid_web20.system.crud import sqlalchemy as sqlalchemy_crud
from pyramid_web20.system.crud.sqlalchemy import ModelCRUD
from pyramid_web20.utils import traverse



class Root:
    __name__ = ""



def admin_root_factory(request):
    """Get the admin object for the routes."""
    admin = Admin.get_admin(request.registry)
    return admin



class Admin(traverse.BreadcrumsResource):
    """Admin interface main object.

    We know what panels are registered on the main admin screen.
    """

    # Root defines where admin interaface lies in the URL space
    __parent__ = Root()
    __name__ = "admin"

    __acl__ = [
        (Allow, 'group:admin', 'view'),
    ]

    def __init__(self):
        self.model_admins = {}

    @classmethod
    def get_admin(cls, registry):
        """Get hold of admin singleton."""
        return registry.settings["pyramid_web20.admin"]

    def scan(self, config, module):
        """Picks up admin definitions from the module."""

        __admin__ = getattr(module, "__admin__", None)

        if not __admin__:
            raise RuntimeError("Admin tried to scan module {}, but it doesn't have __admin__ attribute. The module probably doesn't define any admin objects.".format(module))

        for model_dotted, admin_cls in __admin__.items():

            # Instiate model admin
            try:
                model = config.maybe_dotted(model_dotted)
            except ImportError as e:
                raise ImportError("Tried to initialize model admin for {}, but could not import it".format(model_dotted)) from e

            try:
                model_admin = admin_cls(model)
            except Exception as e:
                raise RuntimeError("Could not instiate model admin {} for model {}".format(admin_cls, model)) from e

            id = getattr(model_admin, "id", None)
            if not id:
                raise RuntimeError("Model admin does not define id {}".format(model_admin))

            # Keep ACL chain intact
            traverse.make_lineage(self, model_admin, id, allow_reinit=True)

            self.model_admins[id] = model_admin

    def get_admin_for_model(self, model):
        for model_admin in self.model_admins.values():
            if model_admin.model == model:
                return model_admin

        raise KeyError("No admin defined for model: {}, got {} ".format(model, self.model_admins.values()))

    def get_admin_resource(self, obj):
        """Get a admin traversable item for a SQLAlchemy object.

        To get admin URL of an SQLAlchemy object::

        :param obj: SQLAlchemy model instance
        """

        assert obj.id
        assert type(obj.id) == int, "Got bad object: {}".str(obj)

        model = obj.__class__
        model_admin = self.get_admin_for_model(model)
        return model_admin[obj.id]

    def get_admin_object_url(self, request, obj):
        """Get URL for viewing the object in admin.

        *obj* must be a model instance which has a registered admin interfaec.
        """
        res = self.get_admin_resource(obj)
        return request.resource_url(res)

    def get_breadcrumbs_title(self):
        return "Admin"

    def __getitem__(self, name):

        # Traverse to models
        model_admin = self.model_admins[name]
        return model_admin


class ModelAdmin(ModelCRUD):
    """Present one model in admin interface."""

    #: URL traversing id
    id = None

    #: Title used in breadcrumbs, other places
    title = None

    def get_admin(self):
        return self.__parent__

    def init_lineage(self):
        """Make sure that all context objects have parent pointers set."""
        super(ModelAdmin, self).init_lineage()

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

    def get_breadcrumbs_title(self):
        if self.title:
            return self.title
        return self.id.capitalize()

    def __getitem__(self, id):

        if id == "panel":
            return self.panel

        return super(ModelCRUD, self).__getitem__(id)


class Listing(sqlalchemy_crud.Listing):
    template = "admin/listing.html"
    base_template = "admin/base.html"



class DefaultModelAdmin(ModelAdmin):
    """Model admin used if the model does not declare any admin."""

    listing = sqlalchemy_crud.Listing(
        title="",
        columns = [
            crud.Column("id", "Id",),
            crud.ControlsColumn()
        ]
    )

    show = crud.Show(
        includes=["id"]
    )
