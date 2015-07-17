"""Support for Alembic SQL migrations."""
import logging

from pyramid.paster import setup_logging
from pyramid.paster import bootstrap

from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker
from alembic import context

from websauna.system.model import Base
from websauna.system.model import DBSession


logger = None


def get_migration_table_name(package_name: str) -> str:
    """Convert Python package name to migration table name."""
    assert type(package_name) == str
    table = package_name.replace(".", "_").lower()
    return "alembic_history_{}".format(table)


def get_class_by_table_name(tablename):
  """Return class reference mapped to table.

  :param tablename: String with name of table.
  :return: Class reference or None.
  """
  for c in Base._decl_class_registry.values():
    if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
      return c


def run_migrations_offline(url, target_metadata, version_table, include_object):
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, version_table=version_table, include_object=include_object)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online(engine, target_metadata, version_table, include_object):
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = engine
    # connectable = engine_from_config(
    #    config.get_section(config.config_ini_section),
    #    prefix='sqlalchemy.',
    #    poolclass=pool.NullPool)

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=version_table,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


def get_sqlalchemy_metadata(package):
    """Get the SQLAlchemy MetaData instance which contains declarative tables only from a certain Python packagek.

    We get all tables which have been registered against the current Base model. Then we grab Base.metadata and drop out all tables which we think are not part of our migration run.
    """

    allowed_tables = []

    # Include all SQLAlchemy models in the local namespace
    for name, klass in Base._decl_class_registry.items():
        if isinstance(klass, _ModuleMarker):
            continue

        if not klass.__module__.startswith(package):
            logger.debug("Skipping SQLAlchemy model %s as out of scope for package %s", klass, package)
            continue

        allowed_tables.append(klass.__table__)

    # Remove metadata table registrations which did not below to the package
    metadata = Base.metadata
    for table in list(metadata.tables.values()):
        if not table in allowed_tables:
            metadata.remove(table)

    return metadata



def run_alembic(package:str):
    """Alembic env.py script entry point for Websauna application.

    Initialize the application, load models and pass control to Alembic migration handler.

    :param package: String of the Python package name whose model the migration concerns.
    """
    global logger
    global version_table

    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config

    # This was -c passed to ws-alembic command
    config_file = config.config_file_name

    setup_logging(config_file)

    # Load the WSGI application, etc.
    env = bootstrap(config_file, options=dict(sanity_check=False))

    # Delay logger creation until we have initialized the logging system
    logger = logging.getLogger(__name__)

    #: Pull out MetaData instance for the system
    target_metadata = get_sqlalchemy_metadata(package)

    # Extract database connection URL from the settings
    url = env["registry"].settings["sqlalchemy.url"]

    # Use live SQLAlchemy engine object for online migrations
    engine = DBSession.get_bind()

    # Each package needs to maintain its own alembic_history table
    version_table = get_migration_table_name(package)

    def include_object(object, name, type_, reflected, compare_to):
        """Determine if the migrations should consider this model or not.

        We are only interested models provided by our package.

        http://dev.utek.pl/2013/ignoring-tables-in-alembic/
        """
        if type_ == "index":
            table_name = object.table.name
        else:
            table_name = object.name

        print(object, type_, table_name)

        model = get_class_by_table_name(table_name)
        if not model:
            # Don't know what's this... let's skip
            return False

        module = model.__module__

        # XXX: This is not very beautiful check but works for now
        return module.startswith(package)

    if context.is_offline_mode():
        run_migrations_offline(url, target_metadata, version_table, include_object)
    else:
        logger.info("Starting online migration engine on database connection {} version history table {}".format(engine, version_table))
        run_migrations_online(engine, target_metadata, version_table, include_object)

    logger.info("All done")


