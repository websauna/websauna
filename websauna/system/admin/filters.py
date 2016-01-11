"""Jinja template filters used in admin UI."""

from pyramid.renderers import render
from pyramid.threadlocal import get_current_request

from jinja2 import contextfilter
from websauna.system.admin.interfaces import IAdmin
from websauna.system.core.breadcrumbs import get_breadcrumb


@contextfilter
def admin_breadcrumbs(jinja_ctx, context, **kw):
    """Render admin interface top breadcrumbs bar."""

    if not context:
        return ""

    request = jinja_ctx.get('request') or get_current_request()
    crumbs = get_breadcrumb(context, request, root_iface=IAdmin)

    assert crumbs, "Could not get breadcrumbs for {}".format(context)

    if len(crumbs) == 1:
        return ""

    return render("templates/admin/breadcrumbs.html", dict(context=context, crumbs=crumbs), request=request)