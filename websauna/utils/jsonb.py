"""JSONB data utilities."""
import datetime
from decimal import Decimal
import copy
import json
import inspect as python_inspect
import iso8601

from sqlalchemy import inspect
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.attributes import set_attribute


import jsonpointer


class BadJSONData(Exception):
    """You tried to save something which cannot be stick into JSON data."""


class BadStoredData(Exception):
    """We found something which is non-JSON like from the database."""


class CannotLookupData(Exception):
    """Member get failed."""

class CannotProcessISO8601(Exception):
    """You passed in a naive datetime without explicit timezone information."""


class NullConverter(object):

    def serialize(self, val):
        return val

    def deserialize(self, val):
        return val


class ISO8601DatetimeConverter(object):
    """Serialize datetime to ISO8601 unless it's None."""

    def serialize(self, val):

        if val is None:
            return val

        assert isinstance(val, datetime.datetime), "Got type {}".format(type(val))

        if not val.tzinfo:
            raise CannotProcessISO8601("datetime lacks timezone information: {}. Please use datetime.datetime.utcnow(datetime.timezone.utc)".format(val))

        return val.isoformat()

    def deserialize(self, val):

        if val is None:
            return val

        return iso8601.parse_date(val)


_marker = object()


class JSONBProperty(object):
    """Define a Python class property which can set/get JSONB field data.

    The location of the propety is defined using JSON Pointer notation.

    - `JSON Pointer Notation specification <https://tools.ietf.org/html/rfc6901>`_

    - Underlying `jsonpointer Python module documentation <http://python-json-pointer.readthedocs.org/en/latest/index.html>`_

    In the case the field value is not yet set and you try to access it, a Falsy valud ``JSONBField.UNDEFINED` is returned.

    You must be aware of JSON data limitations when using JSONB properties

    - All numbers are floats

    - No native support for datetime storage

    :param data_field: The name of the SQLAlchemy field holding JSONB data on this model.

    :param pointer: RFC6901 pointer to the field.

    :param converter: JSON serializer/deserializer. Can be a class or instance with serialize() / deserialize() methods.

    :param graceful: If set, return this value when the member is not found instead of raising exception
    """

    #: Return this value if there is nothing at the end of RFC 6901 pointer
    UNDEFINED = jsonpointer._nothing

    def __init__(self, data_field, pointer, graceful=_marker, converter=NullConverter):
        self.data_field = data_field
        self.pointer = pointer

        # Passed in a class
        if type(converter) == type:
            converter = converter()

        self.converter = converter
        self.graceful = graceful

    def ensure_valid_data(self, obj):
        """Handle freshly created objects and corrupted data more gracefully."""

        if obj is None:
            # TODO: Not sure what is this but gets hit during Sphinx build
            return None

        field = getattr(obj, self.data_field)

        if field is None:
            insp = inspect(obj)

            if insp.persistent or insp.detached:
                raise BadStoredData("Field {} contained None (NULL) - make sure it is initialized with empty dictionary".format(self.data_field))
            else:
                # An object of which field default value is not yet set

                # <sqlalchemy.orm.attributes.InstrumentedAttribute>
                column = getattr(obj.__class__, self.data_field)
                default = column.default.arg
                setattr(obj, self.data_field, default)
                return default

        return field

    def is_graceful(self):
        return self.graceful != _marker

    def __get__(self, obj, objtype=None):
        data = self.ensure_valid_data(obj)
        if data is None:
            # Gets hit by Sphinx build
            return None
        try:
            val = jsonpointer.resolve_pointer(data, self.pointer, default=JSONBProperty.UNDEFINED)
        except jsonpointer.JsonPointerException as e:
            # TODO: update jsonpointer to give more specific errors, this could vbe something else besides member not found
            if self.is_graceful():
                val = self.graceful
            else:
                raise CannotLookupData("Could not find {} on data {}".format(self.pointer, obj))
        return self.converter.deserialize(val)

    def __set__(self, obj, val):

        # TODO: Abstract JsonPointerException when settings a member with missing nested parent dict

        # We need to deepcopy data, so that SQLAlchemy can detect changes. Otherwise nested changes would mutate the dict in-place and SQLAlchemy cannot perform comparison.
        data = copy.deepcopy(self.ensure_valid_data(obj))

        val = self.converter.serialize(val)

        if val is not None:

            # Do some basic data validation, don't let first class objects slip through
            if type(val) not in (str, float, bool, int, dict):
                raise BadJSONData("Cannot update field at {} as it has unsupported type {} for JSONB data".format(self.pointer, type(val)))

        jsonpointer.set_pointer(data, self.pointer, val)

        set_attribute(obj, self.data_field, data)
        # flag_modified(obj, self.data_field)

    @classmethod
    def is_json_property(cls, obj, name):
        """Check if given attribute on an object is JSONBProperty.

        :param obj: Python object

        :return: True or False
        """

        attr = python_inspect.getattr_static(obj, name)
        return isinstance(attr, JSONBProperty)



class _DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(_DecimalEncoder, self).default(o)


def complex_json_dumps(d):
    """Dump JSON so that we handle decimal and dates.

    Decimals are converted to strings.

    Dates are converted to ISO8601.
    """
    return json.dumps(d, cls=_DecimalEncoder)
