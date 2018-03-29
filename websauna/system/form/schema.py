"""Various Colander schema base classes and utililties for forms."""
# Standard Library
import enum
import json
import typing as t

# Pyramid
import colander
import deform  # noQA

#: Backwards compatibility
from .csrf import CSRFSchema  # noQA
from .csrf import add_csrf  # noQA


def validate_json(node, value, **kwargs):
    """Make sure the string content is valid JSON."""

    try:
        json.loads(value)
    except json.JSONDecodeError:
        raise colander.Invalid(node, "Not valid JSON")


def enum_values(source: enum.Enum, default: t.Optional[t.Tuple]=("", "Please choose"), name_transform=str.title) -> t.Iterable[t.Tuple]:
    """Turn Python Enum to key-value pairs lists to be used with selection widgets."""

    def inner():
        if default:
            yield default

        for name, member in source.__members__.items():
            yield (member.value, name_transform(name))

    return list(inner())


def dictify(schema: colander.Schema, obj: object, excludes=()) -> dict:
    """ Return a dictified version of `obj` using schema information.

    The schema will be used to choose what attributes will be
    included in the returned dict.

    Thus, the return value of this function is suitable for consumption
    as a ``Deform`` ``appstruct`` and can be used to pre-populate
    forms in this specific use case.

    Arguments/Keywords

    :param obj:
        An object instance to be converted to a ``dict`` structure.
        This object should conform to the given schema.  For
        example, ``obj`` should be an instance of this schema's
        mapped class, an instance of a sub-class, or something that
        has the same attributes.

    :param exludes: List of node names not to automatically dictify

    Based on colanderalchemy implemetation.
    """
    dict_ = {}

    for node in schema.children:

        if not getattr(node, "dictify_by_default", True):
            # This is set by CSRF field, so that we don't need to manually
            # skip it between object serializations.
            # Not elegant, but convenient.
            continue

        name = node.name
        if name in excludes:
            continue

        value = getattr(obj, name)

        # SQLAlchemy mostly converts values into Python types
        #  appropriate for appstructs, but not always.  The biggest
        #  problems are around `None` values so we're dealing with
        #  those here.  All types should accept `colander.null` so
        #  we mostly change `None` into that.

        if value is None:
            if isinstance(node.typ, colander.String):
                # colander has an issue with `None` on a String type
                #  where it translates it into "None".  Let's check
                #  for that specific case and turn it into a
                #  `colander.null`.
                dict_[name] = colander.null
            else:
                # A specific case this helps is with Integer where
                #  `None` is an invalid value.  We call serialize()
                #  to test if we have a value that will work later
                #  for serialization and then allow it if it doesn't
                #  raise an exception.  Hopefully this also catches
                #  issues with user defined types and future issues.
                try:
                    node.serialize(value)
                except Exception:
                    dict_[name] = colander.null
                else:
                    dict_[name] = value
        else:
            dict_[name] = value

    return dict_


def objectify(schema: colander.Schema, appstruct: dict, context: object, excludes=()):
    """Store incoming appstruct data on an object like SQLAlchemy model instance"""

    for node in schema.children:

        if not getattr(node, "dictify_by_default", True):
            # This is set by CSRF field, so that we don't need to manually
            # skip it between object serializations.
            # Not elegant, but convenient.
            continue

        name = node.name
        if name in excludes:
            continue

        try:
            setattr(context, name, appstruct[name])
        except AttributeError as e:
            raise AttributeError("Could not set attr {} on {} from schema {}".format(name, context, schema)) from e
