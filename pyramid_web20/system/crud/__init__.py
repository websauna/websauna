"""CRUD based on SQLAlchemy and Deform."""


class CRUD:
    listing = None
    view = None
    add = None
    edit = None
    delete = None


class Column:
    def __init__(self, field, name, renderer=None):
        self.field = field
        self.name = name
        self.renderer = renderer


class Listing:

    def __init__(self, columns):
        pass
