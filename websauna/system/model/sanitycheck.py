# Standard Library
import logging
import typing as t

# SQLAlchemy
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import inspect
from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


def _log_error_message(klass: object, engine: object, table: t.Optional[str] = None, column: t.Optional[str] = None):
    instance = 'column' if column else 'table'
    name = column if column else table
    logger.error(
        "Model {klass} declares {instance} {name} which does not exist in database {engine}".format(
            klass=klass,
            instance=instance,
            name=name,
            engine=engine
        )
    )


def is_sane_database(Base, session: Session):
    """Check whether the current database matches the models declared in model base.

    Currently we check that all tables exist with all columns. What is not checked

        * Column types are not verified
        * Relationships are not verified at all (TODO)

    :param Base: Declarative Base for SQLAlchemy models to check
    :param session: SQLAlchemy session bound to an engine
    :return: True if all declared models have corresponding tables and columns.
    """

    engine = session.get_bind()
    iengine = inspect(engine)

    errors = False

    # Get tables currently in the database
    tables = iengine.get_table_names()

    # Go through all SQLAlchemy models
    for name, klass in Base._decl_class_registry.items():

        if isinstance(klass, _ModuleMarker):
            # Not a model
            continue

        # 1. Check if this model declares any tables they exist

        # First try raw table definition
        table = getattr(klass, "__table__", None)
        table = table.name if table is not None else getattr(klass, "__tablename__", None)

        if not table:
            raise RuntimeError("Table definition missing for {name}".format(name=klass.__name__))

        if table not in tables:
            _log_error_message(klass, engine, table)
            errors = True

        # 2. Check that all columns declared by the model exist
        mapper = inspect(klass)

        for column_prop in mapper.attrs:
            if isinstance(column_prop, RelationshipProperty):
                # TODO: Add sanity checks for relations
                continue

            # Iterate all columns the model declares
            for column in column_prop.columns:
                # Just deal with sqlalchemy.Column instances
                if not isinstance(column, Column):
                    continue

                table_name = column.table.name

                # Get columns from the actual table the ORM referes to
                try:
                    columns = [c["name"] for c in iengine.get_columns(table_name)]
                except sqlalchemy.exc.NoSuchTableError:
                    _log_error_message(klass, engine, table_name)
                    errors = True
                    break

                if column.key not in columns:
                    # It is safe to stringify engine where as password should be blanked out by stars
                    _log_error_message(klass, engine, None, column.key)
                    errors = True

    return not errors
