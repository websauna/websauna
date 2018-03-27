"""Jinja template filters used in admin UI."""

# Pyramid
from jinja2 import contextfilter
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request

# Websauna
from websauna.system.admin.interfaces import IAdmin
from websauna.system.core.breadcrumbs import get_breadcrumbs


@contextfilter
def admin_breadcrumbs(jinja_ctx, context, **kw):
    """Render admin interface top breadcrumbs bar."""

    if not context:
        return ""

    request = jinja_ctx.get('request') or get_current_request()
    current_view_name = jinja_ctx.get("current_view_name")
    current_view_url = request.url
    crumbs = get_breadcrumbs(context, request, root_iface=IAdmin, current_view_name=current_view_name, current_view_url=current_view_url)

    assert crumbs, "Could not get breadcrumbs for {}".format(context)

    if len(crumbs) == 1:
        return ""

    return render("admin/breadcrumbs.html", dict(context=context, breadcrumbs=crumbs), request=request)
