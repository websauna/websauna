"""Database default base models and setup."""
import transaction
from pyramid.settings import asbool
from pyramid_tm import resolver
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.schema import MetaData
import zope.sqlalchemy


metadata = MetaData()

#: This is a default SQLAlchemy model base class. Models inhering from this class are automatically registered with the default SQLAlchemy session. You can have your alternative Base class, but in this case you need to bind the Base class session yourself.
Base = declarative_base(metadata=metadata)


def includeme(config):
    """Configure the default database engine and model bindings.

    Reads ``sqlalchemy.*`` settings from the INI file and configures SQLAlchemy engine accordingly.

    :param config:
    :return:
    """
    settings = config.get_settings()
    engine = get_engine(settings)
    dbmaker = get_dbmaker(engine)

    config.add_request_method(
        lambda r: get_session(r.tm, dbmaker),
        'dbsession',
        reify=True
    )

    # TODO: This is alias for hem/db.py used by Horus
    # Remove when got rid of Horus
    config.add_request_method(
        lambda req: req.dbsession,
        'db_session',
        reify=True
    )

    config.include('pyramid_tm')

    # Register UTC timezone enforcer
    if asbool(config.registry.settings.get("websauna.force_utc_on_columns", True)):
        from . import sqlalchemyutcdatetime


def get_session(transaction_manager, dbmaker):
    """Get a new database session."""
    dbsession = dbmaker()
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def get_engine(settings, prefix='sqlalchemy.'):
    # http://stackoverflow.com/questions/14783505/encoding-error-with-sqlalchemy-and-postgresql
    engine = engine_from_config(settings, 'sqlalchemy.', connect_args={"options": "-c timezone=utc"}, client_encoding='utf8')
    return engine


def get_dbmaker(engine):
    dbmaker = sessionmaker()
    dbmaker.configure(bind=engine)
    return dbmaker


def create_dbsession(settings, manager=transaction.manager) -> Session:
    """Creates a new database session and transaction manager which co-ordinates it.

    :param manager: Transaction manager to bound the session. The default is thread local ``transaction.manager``.
    """

    dbmaker = get_dbmaker(get_engine(settings))
    dbsession = get_session(manager, dbmaker)
    return dbsession

