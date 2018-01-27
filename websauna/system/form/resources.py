"""Deform lib resource management."""

# Pyramid
import deform.widget
from zope.interface import implementer

# Websauna
from websauna.system.form.interfaces import IFormResources


default_resources = deform.widget.default_resources

# Make sure pick-a-date widget works out of the box
default_resources["pickadate"][None]["css"] = list(default_resources["pickadate"][None]["css"]) + ["websauna.system:static/pickadate-fixes.css"]


@implementer(IFormResources)
class DefaultFormResources:
    """Default form resources implementation.

    If you need to override or manipulate default form resources you can do it by overriding :py:class:`websauna.system.form.interfaces.IFormResources` utility. See :py:meth:`websauna.system.Initializer.configure_forms` for more inforation.
    """

    def get_default_resources(self):
        return default_resources
