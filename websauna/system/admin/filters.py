from pyramid.renderers import render
from pyramid.threadlocal import get_current_request

from jinja2 import contextfilter

from websauna.system.core import traverse
from . import Admin


@contextfilter
def admin_breadcrumbs(jinja_ctx, context, **kw):
    """Render admin breadcrumbs."""

    if not context:
        return ""

    request = jinja_ctx.get('request') or get_current_request()
    crumbs = traverse.get_breadcrumb(context, request, root=Admin)

    assert crumbs, "Could not get breadcrumbs for {}".format(context)

    if len(crumbs) == 1:
        return ""

    # Fix admin name so we don't confuse this with the menubar
    crumbs[0]["name"] = "Home"

    return render("templates/admin/breadcrumbs.html", dict(context=context, crumbs=crumbs), request=request)