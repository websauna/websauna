"""Helper functions."""
from sqlalchemy import Column
from sqlalchemy import inspect


def get_relationship_for_foreign_key(model: type, column: Column):
    """Check if SQLAlchemy column is a foreign key part of any relationship.

    Handle single foreign keys only - is not tested or designed for complex joins.
    """

    if len(column.foreign_keys) != 1:
        # Too complicated for us...
        return None

    # Peek one item from set, http://stackoverflow.com/questions/59825/how-to-retrieve-an-element-from-a-set-without-removing-it
    for foreign_key in column.foreign_keys:
        break

    mapper = inspect(model)

    for rel in mapper.relationships:
        for col in rel.local_columns:
            if col == column:
                return rel
