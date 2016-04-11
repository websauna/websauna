"""pyramid_layout panel rendering helper.

TODO: This module is on the list of those who will get burial by fire.
"""

from markupsafe import Markup
from pyramid_layout.interfaces import IPanel
from zope.interface import providedBy


# Jinja 2 adoption of render_panel
# TODO: make this configurable in upstream
def render_panel(context, request, name='', *args, **kw):
    """Render a panel.

    TODO: Clean this up

    Renders the named panel, returning a `unicode` object that is the
    rendered HTML for the panel.  The panel is looked up using the current
    context (or the context given as keyword argument, to override the
    context in which the panel is called) and an optional given name
    (which defaults to an empty string).
    The panel is called passing in the current
    context, request and any additional parameters passed into the
    `render_panel` call.  In case a panel isn't found, `None` is returned.
    """

    if not "controls" in kw:
        kw["controls"] = True

    adapters = request.registry.adapters
    panel = adapters.lookup((providedBy(context),), IPanel, name=name)
    assert panel, "Could not find panel {}".format(name)
    return Markup(panel(context, request, *args, **kw))
