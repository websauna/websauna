"""Extra template variables."""
import datetime
import json
from time import ctime as time_ctime
from pyramid.config import Configurator

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
from websauna.system.compat import typing

from websauna.utils import html
from websauna.utils.time import now



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

    # Meke relative time between two timestamps

    now = now.astimezone(tz)

    arrow = Arrow.fromdatetime(now)
    other = Arrow.fromdatetime(datetime.datetime.utcnow())

    return arrow.humanize(other)


@contextfilter
def escape_js(jinja_ctx, context, **kw):
    """Make JSON strings to safe to be embedded inside <script> tag."""
    markup = Markup(html.escape_js(context))
    return markup


@contextfilter
def to_json(jinja_ctx, context, safe=True):
    """Converts Python dict to JSON, safe to be placed inside <script> tag.

    :param context: Takes Python dictionary as input

    :param safe: Set to False to not to run ``escape_js()`` on the resulting JSON. True by default.

    :return: JSON string to be included inside HTML code
    """
    json_ = json.dumps(context)
    if safe:
        return escape_js(jinja_ctx, json_)
    else:
        return json_


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


@contextfilter
def fromtimestamp(jinja_ctx, context, **kw):
    """Convert UNIX datetime to timestamp.

    Example:

    .. code-block:: html

        <p>
            Prestodoctor license expires: {{ prestodoctor.recommendation.expires|fromtimestamp(timezone="US/Pacific")|friendly_time }}
        </p>

    :param context: UNIX timestamps as float as seconds since 1970
    :return: Python datetime object
    """

    tz = kw.get("timezone")
    assert tz, "You need to give an explicitimezone when converting UNIX times to datetime objects"

    # From string to object
    tz = timezone(tz)
    ct = datetime.datetime.fromtimestamp(context, tz=tz)
    return ct


def include_filter(config:Configurator, name:str, func:typing.Callable, renderers=(".html", ".txt",)):
    """Register a new Jinja 2 template filter function.

    Example::

        import jinja2

        @jinja2.contextfilter
        def negative(jinja_ctx:jinja2.runtime.Context, context:object, **kw):
            '''Output the negative number.

            Usage:

                {{ 3|neg }}

            '''
            neg = -context
            return neg


    Then in your initialization:

        include_filter(config, "neg", negative)

    :param config: Pyramid configurator

    :param name: Filter name in templates

    :param func: Python function which is the filter

    :param renderers: List of renderers where the filter is made available

    """

    def _include_filter(name, func):

        def deferred():
            for renderer_name in renderers:
                env = config.get_jinja2_environment(name=renderer_name)
                assert env, "Jinja 2 not configured - cannot add filters"
                env.filters[name] = func

        # Because Jinja 2 engine is not initialized here, only included here, we need to do template filter including asynchronously
        config.action('pyramid_web-include-filter-{}'.format(name), deferred, order=1)

    _include_filter(name, func)


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


    include_filter(config, "friendly_time", friendly_time)
    include_filter(config, "datetime", filter_datetime)
    include_filter(config, "escape_js", escape_js)
    include_filter(config, "timestruct", timestruct)
    include_filter(config, "to_json", to_json)
    include_filter(config, "fromtimestamp", fromtimestamp)


