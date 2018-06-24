"""Database default base models and session setup."""
# Pyramid
import transaction
import zope.sqlalchemy
from pyramid.registry import Registry
from transaction import TransactionManager

# SQLAlchemy
from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.schema import MetaData

# Websauna
from websauna.system.http import Request
from websauna.system.model.interfaces import ISQLAlchemySessionFactory

from .json import init_for_json
from .json import json_serializer


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


@event.listens_for(Base, 'class_instrument', propagate=True)
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


def _get_psql_engine(settings: dict, prefix: str) -> Engine:
    """Create PostgreSQL engine.

    The database engine defaults to SERIALIZABLE isolation level.
    :param settings: Application settings
    :param prefix: Configuration prefixes
    :return: SQLAlchemy Engine
    """
    # http://stackoverflow.com/questions/14783505/encoding-error-with-sqlalchemy-and-postgresql
    engine = engine_from_config(settings, prefix, connect_args={"options": "-c timezone=utc"}, client_encoding='utf8', isolation_level='SERIALIZABLE', json_serializer=json_serializer)
    return engine


def get_engine(settings: dict, prefix: str='sqlalchemy.') -> Engine:
    """Reads config and create a database engine out of it.

    :param settings: Application settings
    :param prefix: Configuration prefixes
    :return: SQLAlchemy Engine
    """
    url = settings.get('sqlalchemy.url')
    if not url:
        raise RuntimeError('sqlalchemy.url missing in the settings')

    if 'postgres' in url:
        engine = _get_psql_engine(settings, prefix)
    else:
        raise RuntimeError('Unknown SQLAlchemy connection URL: {url}'.format(url=url))
    return engine


def get_default_engine(registry: Registry) -> Engine:
    """
    Creates or gets the default database engine using the settings in registry.

    The engine is a singleton and a reference will be stored in the application registry.
    :param registry: the registry
    :return: the created engine
    """
    try:
        engine = registry['websauna.db.default_engine']
    except KeyError:
        engine = registry['websauna.db.default_engine'] = get_engine(registry.settings)

    return engine


def _create_session(transaction_manager: TransactionManager, engine: Engine) -> Session:
    """Create a new database session with Zope transaction manager attached.

    The attached transaction manager takes care of committing the transaction at the end of the request.
    """
    dbsession = Session(bind=engine)
    transaction_manager.retry_attempt_count = 3  # TODO: Hardcoded for now
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    dbsession.transaction_manager = transaction_manager
    return dbsession


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
    engine = get_default_engine(registry)

    if not manager:
        manager = transaction.manager

    if isolation_level != _DEFAULT:
        engine = engine.execution_options(isolation_level=isolation_level)

    dbsession = _create_session(manager, engine)
    return dbsession
