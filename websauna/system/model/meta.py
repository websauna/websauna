"""Database default base models and session setup."""


# Pyramid
import transaction
import zope.sqlalchemy
from pyramid.registry import Registry

# SQLAlchemy
from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
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
        raise RuntimeError("Unknown SQLAlchemy connection URL: {url}".format(url=url))


def create_session_maker(engine):
    """Create database session maker.

    Must be called only once per process.
    """
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine)
    return dbmaker


def create_dbsession(registry: Registry, manager=None) -> Session:
    """Creates a new database using the configured session poooling.

    This is called outside request life cycle when initializing and checking the state of the databases.

    :param manager: Transaction manager to bound the session. The default is thread local ``transaction.manager``.
    """

    assert isinstance(registry, Registry), "The first arg must be registry (Method signature changed)"

    # Make sure dbmaker is created only once per process as it must be
    # per-process for the connection pooling to work.
    # Cache the resulting object on Pyramid registry.
    db_session_maker = getattr(registry, "db_session_maker", None)

    if not db_session_maker:
        engine = get_engine(registry.settings)
        db_session_maker = registry.db_session_maker = create_session_maker(engine)

    if not manager:
        manager = transaction.manager

    dbsession = create_session(manager, db_session_maker)

    # Register zope.sqlalchemy extensino
    # register(dbsession, manager)

    return dbsession


def create_session(transaction_manager, db_session_maker: sessionmaker) -> Session:
    """Create a new database session with Zope transaction manager attached.

    The attached transaction manager takes care of committing the transaction at the end of the request.
    """
    dbsession = db_session_maker()
    transaction_manager.retry_attempt_count = 3  # TODO: Hardcoded for now
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    dbsession.transaction_manager = transaction_manager
    return dbsession
