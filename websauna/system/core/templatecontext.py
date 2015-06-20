"""Extra template variables."""
import datetime

from pyramid.events import BeforeRender
from pyramid.renderers import render
from pyramid.security import effective_principals
from pyramid.settings import asbool
from pyramid.threadlocal import get_current_request
from websauna.system.admin import Admin

from pytz import timezone

from pyramid_jinja2 import IJinja2Environment

from jinja2 import contextfilter
from jinja2 import Markup

from arrow import Arrow

from websauna.utils import html
from websauna.system.model import now


def includeme(config):

    # The site name - used in <title> tag, front page, etc.
    site_name = config.registry.settings["websauna.site_name"]

    # Do not use - use request.route_url("home") to get link to the site root
    site_url = config.registry.settings["websauna.site_url"]

    # Shown in the footer as the site copyright owner
    site_author = config.registry.settings["websauna.site_author"]

    # Shown on the front page below title
    site_tag_line = config.registry.settings["websauna.site_tag_line"]

    # [label] Added beginning of every outgoing email subject
    site_email_prefix = config.registry.settings["websauna.site_email_prefix"]

    # True if this is production set up - can be used in templates to change/hide texts
    site_production = asbool(config.registry.settings.get("websauna.site_production"))

    #: The default site timezone - can be used in templates to translate UTC timetamps
    site_timezone = asbool(config.registry.settings.get("websauna.site_timezone", "UTC"))

    #: Skip CSS in templates in functional test runs to speed them up. This flag is set by py.test fixture.
    testing_skip_css = asbool(config.registry.settings.get("websauna.testing_skip_css", False))

    #: Skip JS in templates loading in functional test runs to speed them up. This flag is set by py.test fixture.
    testing_skip_js = asbool(config.registry.settings.get("websauna.testing_skip_js", False))

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

        event['testing_skip_css'] = testing_skip_css
        event['testing_skip_js'] = testing_skip_css



    config.add_subscriber(on_before_render, BeforeRender)



@contextfilter
def filter_datetime(jinja_ctx, context, **kw):
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