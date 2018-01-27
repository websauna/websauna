# Standard Library
import logging

# SQLAlchemy
import sqlalchemy
from sqlalchemy import inspect
from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


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
        __table__ = getattr(klass, "__table__", None)
        if __table__ is not None:
            table = __table__.name
        else:
            table = getattr(klass, "__tablename__", None)

        if not table:
            raise RuntimeError("Table definition missing for {}".format(table))

        if table not in tables:
            logger.error("Model %s declares table %s which does not exist in database %s", klass, table, engine)
            errors = True

        # 2. Check that all columns declared by the model exist
        mapper = inspect(klass)

        for column_prop in mapper.attrs:
            if isinstance(column_prop, RelationshipProperty):
                # TODO: Add sanity checks for relations
                continue

            # Iterate all columns the model declares
            for column in column_prop.columns:
                table_name = column.table.name

                # Get columns from the actual table the ORM referes to
                try:
                    columns = [c["name"] for c in iengine.get_columns(table_name)]
                except sqlalchemy.exc.NoSuchTableError:
                    logger.error("Model %s declares table %s which does not exist in database %s", klass, table_name, engine)
                    errors = True
                    break

                if column.key not in columns:
                    # It is safe to stringify engine where as password should be blanked out by stars
                    logger.error("Model %s declares column %s which does not exist in database %s", klass, column.key, engine)
                    errors = True

    return not errors
