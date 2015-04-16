from .base import CRUD


class SQLALchemyCRUD(CRUD):

    model = None

    def get_all(self):
        pass
