"""Extra template variables."""
import datetime

from pyramid.events import BeforeRender
from pyramid.renderers import render
from pyramid.settings import asbool
from pyramid.threadlocal import get_current_request

from pytz import timezone

from pyramid_jinja2 import IJinja2Environment

from jinja2 import contextfilter
from jinja2 import Markup

from arrow import Arrow

from pyramid_web20.utils import html
from pyramid_web20.models import now


def includeme(config):

    site_name = config.registry.settings["pyramid_web20.site_name"]
    site_url = config.registry.settings["pyramid_web20.site_url"]
    site_author = config.registry.settings["pyramid_web20.site_author"]
    site_tag_line = config.registry.settings["pyramid_web20.site_tag_line"]
    site_email_prefix = config.registry.settings["pyramid_web20.site_email_prefix"]
    site_production = asbool(config.registry.settings.get("pyramid_web20.site_production"))
    site_timezone = asbool(config.registry.settings.get("pyramid_web20.site_timezone", "UTC"))

    def on_before_render(event):
        # Augment Pyramid template renderers with these extra variables
        event['site_name'] = site_name
        event['site_url'] = site_url
        event['site_author'] = site_author
        event['site_tag_line'] = site_tag_line
        event['site_now'] = now
        event['site_email_prefix'] = site_email_prefix
        event['site_production'] = site_production
        event['site_timezone'] = site_timezone

    config.add_subscriber(on_before_render, BeforeRender)



@contextfilter
def _datetime(jinja_ctx, context, **kw):
    """Format datetime in a certain timezone."""
    now = context

    if not now:
        return ""

    tz = kw.get("timezone", None)
    if tz:
        tz = timezone(tz)
    else:
        tz = datetime.timezone.utc

    locale = kw.get("locale", "en_US")

    arrow = Arrow.fromdatetime(now, tzinfo=tz)

    # Convert to target timezone
    tz = kw.get("target_timezone")
    if tz:
        arrow = arrow.to(tz)
    else:
        tz = arrow.tzinfo

    format = kw.get("format", "YYYY-MM-DD HH:mm")

    text = arrow.format(format, locale=locale)

    if kw.get("show_timezone"):
        text = text + " ({})".format(tz)

    return text


@contextfilter
def friendly_time(jinja_ctx, context, **kw):
    """Format timestamp in human readable format.

    * Context must be a datetimeobject

    * Takes optional keyword argument timezone which is a timezone name as a string. Assume the source datetime is in this timezone.
    """

    now = context

    if not now:
        return ""

    tz = kw.get("source_timezone", None)
    if tz:
        tz = timezone(tz)
    else:
        tz = datetime.timezone.utc

    arrow = Arrow.fromdatetime(now, tzinfo=tz)

    other = Arrow.fromdatetime(datetime.datetime.now(tz=tz))

    return arrow.humanize(other)


@contextfilter
def escape_js(jinja_ctx, context, **kw):
    """Make JSON strings to safe to be embedded inside <script> tag."""
    markup = Markup(html.escape_js(context))
    return markup


@contextfilter
def timestruct(jinja_ctx, context, **kw):
    """Render both humanized time and accurate time.

    * show_timezone

    * target_timezone

    * source_timezone

    * format
    """

    if not context:
        return ""

    assert type(context) in (datetime.datetime, datetime.time,)

    request = jinja_ctx.get('request') or get_current_request()
    if not jinja_ctx:
        return ""

    kw = kw.copy()
    kw["time"] = context
    kw["format"] = kw.get("format") or "YYYY-MM-DD HH:mm"

    return Markup(render("core/timestruct.html", kw, request=request))