"""JSONB data utilities."""
import inspect
from decimal import Decimal
import json

from sqlalchemy.ext.indexable import index_property


class _DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(_DecimalEncoder, self).default(o)


def complex_json_dumps(d):
    """Dump JSON so that we handle decimal and dates.

    Decimals are converted to strings.
    """
    return json.dumps(d, cls=_DecimalEncoder)


def is_index_property(obj: object, name: str) -> bool:
    """Check if an object property is index_property like.

    This is needed to correctly generate Colander schema for index_property in SQLAlchemy models.
    """
    # http://docs.sqlalchemy.org/en/rel_1_1/changelog/migration_11.html#new-indexable-orm-extension
    attr = inspect.getattr_static(obj, name)
    return isinstance(attr, index_property)

