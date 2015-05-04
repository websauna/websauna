import inspect
import logging
import colander
from colanderalchemy.schema import SQLAlchemySchemaNode
from pyramid_web20.utils.jsonb import JSONBProperty


logger = logging.getLogger(__name__)


class PropertyAwareSQLAlchemySchemaNode(SQLAlchemySchemaNode):
    """Allow forming of JSON'ed properties besides SQL Alchemy fields."""

    def dictify(self, obj):
        """ Return a dictified version of `obj` using schema information.

        The schema will be used to choose what attributes will be
        included in the returned dict.

        Thus, the return value of this function is suitable for consumption
        as a ``Deform`` ``appstruct`` and can be used to pre-populate
        forms in this specific use case.

        Arguments/Keywords

        obj
            An object instance to be converted to a ``dict`` structure.
            This object should conform to the given schema.  For
            example, ``obj`` should be an instance of this schema's
            mapped class, an instance of a sub-class, or something that
            has the same attributes.
        """
        dict_ = {}
        for node in self:

            name = node.name
            try:
                if JSONBProperty.is_json_property(obj, name):
                    value = getattr(obj, name)
                else:
                    getattr(self.inspector.column_attrs, name)
                    value = getattr(obj, name)

            except AttributeError:
                try:
                    prop = getattr(self.inspector.relationships, name)
                    if prop.uselist:
                        value = [self[name].children[0].dictify(o)
                                 for o in getattr(obj, name)]
                    else:
                        o = getattr(obj, name)
                        value = None if o is None else self[name].dictify(o)
                except AttributeError:
                    # The given node isn't part of the SQLAlchemy model
                    msg = 'SQLAlchemySchemaNode.dictify: %s not found on %s'
                    logger.debug(msg, name, self)
                    continue

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
                    except:
                        dict_[name] = colander.null
                    else:
                        dict_[name] = value
            else:
                dict_[name] = value

        return dict_