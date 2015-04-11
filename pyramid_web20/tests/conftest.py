"""Support for reading Pyramid configuration files and having rollbacked transactions in tests.

https://gist.github.com/inklesspen/4504383
"""


import os

import pytest

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid_web20.models import DBSession
from pyramid_web20.models import Base

#: Make sure py.test picks this up
from pyramid_web20.tests.functional import web_server  # noqa


@pytest.fixture(scope='session')
def ini_settings(request):

    if not getattr(request.config.option, "ini", None):
        raise RuntimeError("You need to give --ini test.ini command line option to py.test to find our test settings")

    config_uri = os.path.abspath(request.config.option.ini)
    setup_logging(config_uri)
    config = get_appsettings(config_uri)

    return config


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

def pytest_addoption(parser):
    parser.addoption("--ini", action="store", metavar="INI_FILE", help="use INI_FILE to configure SQLAlchemy")
