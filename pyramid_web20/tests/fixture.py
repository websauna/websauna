"""Support for having fixture data in tests.

https://gist.github.com/inklesspen/4504383
"""

import pytest

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid_web20.models import DBSession
from pyramid_web20.models import Base


@pytest.fixture(scope='session')
def appsettings(request):

    if not hasattr(request.config.option, "ini"):
        raise RuntimeError("You need to give --ini test.ini command line option to py.test to find our test settings")

    config_uri = os.path.abspath(request.config.option.ini)
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    return settings


@pytest.fixture(scope='session')
def sqlengine(request, appsettings):
    engine = engine_from_config(appsettings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    def teardown():
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture()
def dbtransaction(request, sqlengine):
    connection = sqlengine.connect()
    transaction = connection.begin()
    DBSession.configure(bind=connection)

    def teardown():
        transaction.rollback()
        connection.close()
        DBSession.remove()

    request.addfinalizer(teardown)

    return connection

