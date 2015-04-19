from pyramid.view import view_config

from . import Listing
from . import CRUD




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

    def get_columns(self):
        return self.get_crud().listing.columns

    def listing(self):
        template = self.context.template
        base_template = self.context.base_template

        if not base_template:
            raise RuntimeError("CRUD listing doesn't define base template {}".format(self.context))

        columns = self.get_columns()

        if not columns:
            raise RuntimeError("CRUD listing doesn't not define any columns: {}".format(self.context))

        for c in columns:
            if not c.header_template:
                raise RuntimeError("header_template missing for column: {}".format(c))
            print(c.header_template)

        listing = self.get_listing()

        query = listing.get_query(self)

        count = self.context.get_count(query)

        # TODO: Paginate

        title = self.context.title
        return dict(title=title, count=count, columns=columns, base_template=base_template, query=query)
