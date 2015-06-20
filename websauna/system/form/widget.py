"""Extra widgets.

Mostly for high level integration.
"""
from colander import null, string_types
import deform
from deform.widget import _normalize_choices
from websauna.system.model import DBSession


class RelationshipCheckboxWidget(deform.widget.CheckboxChoiceWidget):
    """Choose a group of relationships.

    TODO: This is a hack using the default ColanderAlchemy dictify() format which dumps the whole object in relationship as dictionary for us. We are only interested in the relationship object ids. Fix this so that Colander schema can give us list of ids, or even SQLAlchemy model instances themselves.
    """

    #: The model which we are using as the base for the queries
    model = None

    template = 'checkbox_choice'
    readonly_template = 'readonly/checkbox_choice'

    #: callable(obj) which translates raw SQLAlchemy instance to a tuple (id, human readable label)
    make_entry = lambda obj: (obj.id, str(obj.id))

    #: callable(obj) translate SQLAlchemy object to form appstruct format.
    dictify = None

    def make_entry(self, obj):
        return (obj.id, str(obj.id))

    def make_id(self, dict_):
        """Map ColanderAlchemy dictionary to a checkbox value.

        Note that ids must be always str() or checkboxes loses their value on validation, as passed in tmpl_values changes.
        """
        return str(dict_["id"])

    @property
    def values(self):
        query = self.get_query()
        return [self.make_entry(obj) for obj in query.all()]

    def get_query(self):
        """Get the query which populates all the available choices."""
        assert self.model, "No model set"
        return DBSession.query(self.model)

    def get_objects(self, id_list):
        """We get a list of ids from the form post. Convert them to saveable SQL objects.

        Override this if you use custom ids.
        """
        query = self.get_query()
        objects = query.filter(self.model.id.in_(id_list)).all()
        return objects

    def serialize(self, field, cstruct, **kw):

        # Assume cstruct is colanderalchemy dictify() result of relationshipfield
        # [{'id': '1', 'name': 'admin', 'description': <colander.null>, 'group_data': <colander.null>}]

        if cstruct in (null, None):
            cstruct = ()

        cstruct = [self.make_id(dict_) for dict_ in cstruct]

        readonly = kw.get('readonly', self.readonly)
        values = kw.get('values', self.values)

        kw['values'] = _normalize_choices(values)

        template = readonly and self.readonly_template or self.template
        tmpl_values = self.get_template_values(field, cstruct, kw)

        return field.renderer(template, **tmpl_values)

    def fix_deserialize_type(self, obj):
        dict_ = self.dictify(obj)
        dict_["_orig"] = obj
        return dict_

    def deserialize(self, field, pstruct):

        if pstruct is null:
            return null
        if isinstance(pstruct, string_types):
            return (pstruct,)

        der = [self.fix_deserialize_type(obj) for obj in self.get_objects(pstruct)]

        return der