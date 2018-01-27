"""Support for Alembic SQL migrations.

1. Each Python package needs to get its own alembic_history table

2. In "objects to consider" function we resolve the object's package and compare whether it is the package for which we try to create migrations for

3. All migration scripts live inside the package, in alembic/ folder next to setup.py

"""

# Standard Library
import logging
import typing as t

# SQLAlchemy
from alembic import context
from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker
from sqlalchemy.testing.schema import Table

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.cmdline import setup_console_logging
from websauna.system.model.meta import Base


#: Defined later because of initialization order
logger = None


def get_migration_table_name(allowed_packages: t.List, current_package_name) -> str:
    """Convert Python package name to migration table name."""

    package_name = allowed_packages[0]
    if package_name == "all":
        package_name = current_package_name

    table = package_name.replace(".", "_").lower()
    return "alembic_history_{}".format(table)


def get_class_by_table(table: Table) -> type:
    """Return class reference mapped to table.

    :param tablename: String with name of table.
    :return: Class reference or None.
    """
    for c in Base._decl_class_registry.values():
        model_table = getattr(c, "__table__", None)

        # We need to compare by names, because drop declarations use different table objects and eq comparison fails
        if model_table is not None:
            if model_table.name == table.name:
                return c

    return None


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
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        version_table=version_table,
        include_object=include_object,
        compare_types=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online(engine, target_metadata, version_table, include_object):
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = engine

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=version_table,
            include_object=include_object,
            compare_type=True,  # http://stackoverflow.com/a/17176843/315168
        )

        with context.begin_transaction():
            context.run_migrations()


def consider_class_for_migration(klass: type, allowed_packages: t.List) -> bool:

    if allowed_packages[0] == "all":
        return True

    if any(klass.__module__.startswith(pkg) for pkg in allowed_packages):
        return True

    logger.debug("Skipping SQLAlchemy model %s as out of scope for packages %s", klass, allowed_packages)
    return False


def consider_module_for_migration(mod: str, allowed_packages: t.List) -> bool:
    """
    :param mod: Dotted name to a module
    :param allowed_packages: List of allowed packages
    :return:
    """

    if allowed_packages[0] == "all":
        return True

    return any(mod.startswith(pkg) for pkg in allowed_packages)


def get_sqlalchemy_metadata(allowed_packages: t.List):
    """Get the SQLAlchemy MetaData instance which contains declarative tables only from a certain Python packagek.

    We get all tables which have been registered against the current Base model. Then we grab Base.metadata and drop out all tables which we think are not part of our migration run.
    """

    allowed_tables = []

    # Include all SQLAlchemy models in the local namespace
    for name, klass in Base._decl_class_registry.items():

        if isinstance(klass, _ModuleMarker):
            continue

        if not consider_class_for_migration(klass, allowed_packages):
            continue

        allowed_tables.append(klass.__table__)

    # Remove metadata table registrations which did not below to the package
    metadata = Base.metadata
    for table in list(metadata.tables.values()):
        if table not in allowed_tables:
            metadata.remove(table)

    return metadata


def parse_allowed_packages(current_package):
    """Return list of package names we want to consider from Alembic extra arguments."""

    # Extra -x arguments passed to Alembic
    extra = context.get_x_argument(as_dictionary=True)

    # XXX: Make this a proper command line switch when writing more refined Alembic front end
    packages = extra.get("packages", current_package)
    packages = packages.split(",")

    if packages == "all":
        # Force Alembic to consider all packages
        logger.info("Considering migrations for models in all Python packages")
    else:
        logger.info("Considering migrations for models in Python packages %s", packages)

    return packages


def run_alembic(package: str):
    """Alembic env.py script entry point for Websauna application.

    Initialize the application, load models and pass control to Alembic migration handler.

    :param package: String of the Python package name whose model the migration concerns. E.g. the name of the current Websauna package.
    """
    global logger
    global version_table

    current_package = package

    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config

    # This was -c passed to ws-alembic command
    config_file = config.config_file_name

    # Alembic always uses console logging
    setup_console_logging(logging.INFO)

    # Load the WSGI application, etc.
    request = init_websauna(config_file)
    engine = request.dbsession.get_bind()

    # Delay logger creation until we have initialized the logging system
    logger = logging.getLogger(__name__)

    # Extract database connection URL from the settings
    url = request.registry.settings["sqlalchemy.url"]

    allowed_packages = parse_allowed_packages(current_package)

    #: Pull out MetaData instance for the system
    target_metadata = get_sqlalchemy_metadata(allowed_packages)

    # Each package needs to maintain its own alembic_history table
    version_table = get_migration_table_name(allowed_packages, current_package)

    def include_object(object, name, type_, reflected, compare_to):
        """
        """
        # Try to figure out smartly table from different object types
        if type_ in ("index", "column", "foreign_key_constraint", "unique_constraint"):
            table_name = object.table.name
            table = object.table
        elif type_ == "table":
            table_name = object.name
            table = object
        else:
            raise RuntimeError("Don't know how to check type for migration inclusion list: {}".format(type_))

        model = get_class_by_table(table)
        if not model:
            # Don't know what's this... let's skip
            logger.info("No model available: %s %s %s", object, type_, table_name)
            return False

        module = model.__module__

        # XXX: This is not very beautiful check but works for now
        return consider_module_for_migration(module, allowed_packages)

    if context.is_offline_mode():
        run_migrations_offline(url, target_metadata, version_table, include_object)
    else:
        logger.info("Starting online migration engine on database connection {} version history table {}".format(engine, version_table))
        run_migrations_online(engine, target_metadata, version_table, include_object)

    # TODO: If a migration file is written, post-edit it and add websauna import

    logger.info("All done")
