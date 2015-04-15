"""JSONB data utilities."""
from sqlalchemy import inspect
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.attributes import set_attribute


import jsonpointer


class BadJSONData(Exception):
    """You tried to save something which cannot be stick into JSON data."""


class BadStoredData(Exception):
    """We found something which is non-JSON like from the database."""


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
    """

    #: Return this value if there is nothing at the end of RFC 6901 pointer
    UNDEFINED = jsonpointer._nothing

    def __init__(self, data_field, pointer):
        self.data_field = data_field
        self.pointer = pointer

    def ensure_valid_data(self, obj):
        """Handle freshly created objects and corrupted data more gracefully."""

        field = getattr(obj, self.data_field)

        if field is None:
            insp = inspect(obj)

            if insp.persistent or insp.detached:
                raise BadStoredData("Field {} contained None (NULL) - make sure it is initialized with empty dictionary".format(self.data_field))
            else:
                # An object of which field default value is not yet set
                data = {}
                setattr(obj, self.data_field, data)
                return data

        return field

    def __get__(self, obj, objtype=None):
        data = self.ensure_valid_data(obj)
        return jsonpointer.resolve_pointer(data, self.pointer, default=JSONBProperty.UNDEFINED)

    def __set__(self, obj, val):

        # TODO: Abstract JsonPointerException when settings a member with missing nested parent dict

        if type(val) not in (str, float, bool, int):
            raise BadJSONData("Cannot update field at {} as it has unsupported type {} for JSONB data".format(self.pointer, type(val)))

        data = self.ensure_valid_data(obj).copy()
        jsonpointer.set_pointer(data, self.pointer, val)

        # Hint SQLAlchemy that data is dirty now
        set_attribute(obj, self.data_field, data)
