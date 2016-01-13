import colander
import deform
from colander.compat import is_nonstr_iter

from websauna.compat.typing import Union
from websauna.compat.typing import Callable


def defer_widget_values(widget: type, values_callback: Callable, **kwargs) -> deform.widget.Widget:
    """Allow select or checkbox widget values construction deferred during the execution time.

    :param widget: Any Deform widget class, see :py:class:`deform.widget.Widget`
    :param value_callback: This callable(node, kw) is called deferredly by Colander
    :param kwargs: Passed to the widget constructed
    """

    _widget = widget

    @colander.deferred
    def _inner(node, kw):
        widget = _widget(values=values_callback(node, kw))
        return widget

    return _inner


class UUID(colander.String):
    """UUID field for Colander.

    See also :py:class`websauna.system.form.widgets.FriendlyUUIDWidget`.
    """

    def serialize(self, node, appstruct):
        # Assume widgets can handle raw UUID object
        return appstruct


class TuplifiedModel(colander.TupleSchema):
    """Present one model instance as (id, name) tuple."""

    id = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())


class TuplifiedModelSequence(colander.Sequence):

    def serialize(self, node, appstruct, accept_scalar=None):
        """Convert instance of SQLAlchemy objects to list of tuples or select/checkbox widgets."""

        if appstruct is colander.null:
            return colander.null

        def callback(subnode, subappstruct):
            return subnode.serialize(subappstruct)

        return self._impl(node, appstruct, callback, accept_scalar)

    def deserialize(self, node, cstruct, accept_scalar=None):
        """Convert incoming (id,) tuples back to sequence of SQLAlchemy objects."""

        import pdb ; pdb.set_trace()

        if cstruct is colander.null:
            return colander.null

        def callback(subnode, subcstruct):
            return subnode.deserialize(subcstruct)

        return self._impl(node, cstruct, callback, accept_scalar)



class TuplifiedModelSequenceSchema(colander.SequenceSchema):
    """Presents a node of sequence of SQLAlchemy objects.

    Convert SQL model to a list of (id, name) tuples.

    This allows SQLAlchemy models to be directly used with :py:class:`deform.widget.CheckboxChoiceWidget` and co.

    Input: A list of SQLAlchemy model instances

    Output: [(id, name),...] list of pairs
    """

    def __init__(self, *args, **kw):
        super(TuplifiedModelSequenceSchema, self).__init__(*args, **kw)

        child = self.children[0]
        assert isinstance(child, TuplifiedModel)


