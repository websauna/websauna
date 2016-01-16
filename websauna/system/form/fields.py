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
