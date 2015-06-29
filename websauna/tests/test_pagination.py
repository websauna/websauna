import transaction

from websauna.system import  crud
from websauna.system.crud import views


def prepare_sample_crud(config):
    """
    :param config:
    """


    class CRUD(crud.CRUD):
        pass

    class Listing(views.Listing):
        pass

    config.add_view()

def xxx_test_crud_zero_items(web_server, browser, dbsession, init):
    """The first user can open the admin page."""

    crud = prepare_crud()

