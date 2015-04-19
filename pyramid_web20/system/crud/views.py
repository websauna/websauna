"""

collanderalchemy: colanderalchemy.readthedocs.org/en/latest/

"""
from pyramid.view import view_config

import deform
import colanderalchemy

from . import Listing
from . import CRUD
from . import Instance



class CRUDViewController:
    """An abstract base class for CRUD views.

    These views cannot exist in the application alone, because they need Pyramid's router ``route_name`` to tell where these views exist in the application URL space.

    To have CRUD controller for any model in your application

    1) Subclass this

    2) Add @view_config directives for all methods (see user.adminviews for example)
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_crud(self):
        return self.context.__parent__

    def get_listing(self):
        """Get hold of Listing object."""
        return self.get_crud().listing

    def get_query(self):
        """Get SQLAlchemy query used in this CRUD listing.

        This can include filtering e.g. request user, crud parameters, so on.
        """
        return self.get_crud().listing.get_query()

    def get_show_form(self):
        raise NotImplementedError("Subclass must implement")

    def get_columns(self):
        return self.get_crud().listing.columns

    def listing(self, base_template):
        """View for listing objects."""
        template = self.context.template

        if not base_template:
            raise RuntimeError("CRUD listing doesn't define base template {}".format(self.context))

        columns = self.get_columns()

        if not columns:
            raise RuntimeError("CRUD listing doesn't not define any columns: {}".format(self.context))

        for c in columns:
            if not c.header_template:
                raise RuntimeError("header_template missing for column: {}".format(c))

        listing = self.get_listing()

        crud = listing.get_crud()

        query = listing.get_query(self)

        count = self.context.get_count(query)

        # TODO: Paginate

        title = self.context.title
        return dict(title=title, count=count, columns=columns, base_template=base_template, query=query, crud=crud)

    def show(self, base_template):
        """View for showing an individual object."""
        instance = self.context
        assert isinstance(instance, Instance)

        obj = instance.obj
        template = self.context.template

        if not base_template:
            raise RuntimeError("CRUD listing doesn't define base template {}".format(self.context))

        form = self.get_show_form("show")
        appstruct = form.schema.dictify(obj)
        rendered_form = form.render(appstruct, readonly=True)

        title = instance.get_title()

        crud = self.get_crud()

        buttons = dict(edit=True, delete=True)

        return dict(form=rendered_form, instance=instance, obj=obj, title=title, crud=crud, base_template=base_template, buttons=buttons)



class SQLAlchemyCRUDViewController(CRUDViewController):

    def get_show_form(self, type):
        obj = self.context.obj
        show = self.get_crud().show
        includes = show.includes
        schema = colanderalchemy.SQLAlchemySchemaNode(obj.__class__, includes=includes)

        form = deform.Form(schema)
        return form
