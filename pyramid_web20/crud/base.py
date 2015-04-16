"""CRUD based on SQLAlchemy and Deform."""

from pyramid_web20.models import DBSession


class CRUD:
    listing = None
    view = None
    add = None
    edit = None
    delete = None



class Listing:
    pass



class SQLALchemyCRUD(CRUD):

    model = None

    def get_all(self):
        return
