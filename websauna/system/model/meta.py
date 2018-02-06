"""Database default base models and session setup."""
from typing import Callable

import transaction

from sqlalchemy import engine_from_config
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.schema import MetaData
from sqlalchemy import event

from pyramid.registry import Registry
import zope.sqlalchemy
from transaction import TransactionManager

from websauna.system.http import Request
from websauna.system.model.interfaces import ISQLAlchemySessionFactory

from .json import json_serializer
from .json import init_for_json

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.readthedocs.org/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


metadata = MetaData(naming_convention=NAMING_CONVENTION)

#: This is a default SQLAlchemy model base class. Models inhering from this class are automatically registered with the default SQLAlchemy session. You can have your alternative Base class, but in this case you need to bind the Base class session yourself.
Base = declarative_base(metadata=metadata)


@event.listens_for(Base, "class_instrument", propagate=True)
def _on_model_registered(cls):
    """Intercept SQLAlchemy model creation (instrumentation).

    Insert event listeners that allow JSON values play nicely.
    """
    init_for_json(cls)


def includeme(config):
    """Hook up database initialization and SQLAlchemy global setup."""

    config.add_request_method(
        request_session_factory,
        'dbsession',
        reify=True
    )

    config.add_request_method(
        get_request_tm,
        'transaction_manager',
        reify=True
    )


def request_session_factory(request: Request) -> Session:
    """Look SQLAlchemy session creator."""
    session = request.registry.queryAdapter(request, ISQLAlchemySessionFactory)
    assert session, "No configured ISQLAlchemySessionFactory"
    return session


def get_request_tm(request: Request):
    """Get the underlying transaction manager."""
    return request.dbsession.transaction_manager


def create_transaction_manager_aware_dbsession(request: Request) -> Session:
    """Defaut database factory for Websauna.

    Looks up database settings from the INI and creates an SQLALchemy session based on the configuration. The session is terminated on the HTTP request finalizer.
    """
    dbsession = create_dbsession(request.registry, request.tm)

    def terminate_session(request):
        # Close db session at the end of the request and return the db connection back to the pool
        dbsession.close()

    request.add_finished_callback(terminate_session)

    return dbsession


def _get_psql_engin(settings, prefix):
    """Create PostgreSQL engine.

    The database engine defaults to SERIALIZABLE isolation level.
    :param settings:
    :param prefix:
    :return:
    """
    # http://stackoverflow.com/questions/14783505/encoding-error-with-sqlalchemy-and-postgresql
    engine = engine_from_config(settings, 'sqlalchemy.', connect_args={"options": "-c timezone=utc"}, client_encoding='utf8', isolation_level='SERIALIZABLE', json_serializer=json_serializer)
    return engine


def _get_sqlite_engine(settings, prefix):
    engine = engine_from_config(settings, 'sqlalchemy.', isolation_level='SERIALIZABLE')
    return engine


def get_engine(settings: dict, prefix='sqlalchemy.') -> Engine:
    """Reads config and create a database engine out of it."""

    url = settings.get("sqlalchemy.url")

    if not url:
        raise RuntimeError("sqlalchemy.url missing in the settings")

    if "sqlite" in url:
        return _get_sqlite_engine(settings, prefix)
    elif "postgres" in url:
        return _get_psql_engin(settings, prefix)
    else:
        raise RuntimeError("Unknown SQLAlchemy connection URL: {}",format(url))


_DEFAULT = object()


def create_dbsession(registry: Registry, manager: TransactionManager=None, *, isolation_level=_DEFAULT) -> Session:
    """Creates a new database using the configured session pooling.

    This is called outside request life cycle when initializing and checking the state of the databases.

    :param registry: the application registry
    :param manager: Transaction manager to bound the session. The default is thread local ``transaction.manager``.
    :param isolation_level: To set a custom isolation level for this session
    """

    if not isinstance(registry, Registry):
        raise TypeError("The first arg must be registry (Method signature changed)")

    # Make sure *engine* is created only once per process as it must be global
    # in order to connection pooling to work properly.
    # http://docs.sqlalchemy.org/en/latest/core/pooling.html#connection-pool-configuration
    try:
        engine = registry.db_engine
    except AttributeError:
        engine = registry.db_engine = get_engine(registry.settings)

    if not manager:
        manager = transaction.manager

    if isolation_level != _DEFAULT:
        engine = engine.execution_options(isolation_level=isolation_level)

    dbsession = _create_session(manager, engine)
    return dbsession


def _create_session(transaction_manager: TransactionManager, engine: Engine) -> Session:
    """Create a new database session with Zope transaction manager attached.

    The attached transaction manager takes care of committing the transaction at the end of the request.
    """
    dbsession = Session(bind=engine)
    transaction_manager.retry_attempt_count = 3  # TODO: Hardcoded for now
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    dbsession.transaction_manager = transaction_manager
    return dbsession
