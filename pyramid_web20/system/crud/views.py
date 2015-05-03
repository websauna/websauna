"""

collanderalchemy: colanderalchemy.readthedocs.org/en/latest/

"""
from pyramid.view import view_config

import deform
import colanderalchemy

from . import CRUD
from . import Resource

from . import sqlalchemy



class Listing:
    """CRUD listing view base class.

    ``self.context`` points to ``CRUD`` instance.
    """

    #: If the child class is not overriding the rendering loop, point this to a template which provides the page frame and ``crud_content`` block.
    base_template = None

    #: Instance of pyramid_web20.crud.listing.Table
    table = None

    def __init__(self, context, request):

        #: Context points to CRUD instance
        self.context = context
        self.request = request

    def get_model(self):
        return self.context.get_model()

    def get_query(self):
        """Get SQLAlchemy query used in this CRUD listing.

        This can include filtering e.g. request user, crud parameters, so on.
        """
        return self.context.get_query()

    def get_count(self, query):
        """Calculate total item count based on query."""
        return query.count()

    def order_query(self, query):
        return query

    @view_config(context=sqlalchemy.ModelCRUD, renderer="crud/listing.html", permission='view')
    def listing(self):
        """View for listing all objects."""

        crud = self.context

        table = self.table
        columns = table.get_columns()

        # Some pre-render sanity checks

        if not columns:
            raise RuntimeError("CRUD listing doesn't not define any columns: {}".format(self.context))

        for c in columns:
            if not c.header_template:
                raise RuntimeError("header_template missing for column: {}".format(c))

        query = self.get_query()
        count = self.get_count(query)
        query = self.order_query(query)
        base_template = self.base_template

        # TODO: Paginate

        title = self.context.title
        return dict(title=title, count=count, columns=columns, base_template=base_template, query=query, crud=crud)



class Show:

    #: If the child class is not overriding the rendering loop, point this to a template which provides the page frame and ``crud_content`` block.
    base_template = None

    includes = ["id",]

    def __init__(self, context, request):

        #: Context points to ModelResource instance
        self.context = context
        self.request = request

    def get_form(self):
        obj = self.context.obj
        includes = self.includes
        schema = colanderalchemy.SQLAlchemySchemaNode(obj.__class__, includes=includes)
        form = deform.Form(schema)
        return form

    def get_crud(self):
        return self.context.__parent__

    @view_config(context=sqlalchemy.Resource, name="show", renderer="crud/show.html", permission='view')
    def show(self):
        """View for showing an individual object."""
        instance = self.context

        obj = instance.obj
        base_template = self.base_template

        form = self.get_form()
        appstruct = form.schema.dictify(obj)
        rendered_form = form.render(appstruct, readonly=True)

        title = instance.get_title()

        crud = self.get_crud()

        buttons = dict(edit=False, delete=False)

        return dict(form=rendered_form, instance=instance, obj=obj, title=title, crud=crud, base_template=base_template, buttons=buttons)
