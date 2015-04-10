"""JSONB data utilities."""
import jsonpointer


class JSONBField(object):
    """Define a Python class property which can set/get JSONB field data.

    The location of the propety is defined using JSON Pointer notation, https://tools.ietf.org/html/rfc6901

    In the case the field value is not yet set and you try to access it, a Falsy valud ``JSONBField.UNDEFINED`` is returned.

    :param data_field: The name of the SQLAlchemy field holding JSONB data on this model.

    :param path: RFC6901 path to the field.
    """

    UNDEFINED = jsonpointer._nothing

    def __init__(self, data_field, path):
        self.data_field = data_field
        self.path = path

    def __get__(self, obj, objtype=None):
        field = getattr(obj, self.name)
        return jsonpointer.resolve_pointer(field, self.path, defaut=JSONBField.UNDEFINED)

    def __set__(self, obj, val):
        assert type(val) in (str, float, bool, int), "Cannot update field {} as it has unsupported type {} for JSONB data".format(self.name, type(val))
        field = getattr(obj, self.name)
        jsonpointer.set_pointer(field, self.path, val)
