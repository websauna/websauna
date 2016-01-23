"""Websauna template filters ."""
import datetime
import json

from pyramid.config import Configurator
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request

from pytz import timezone
from jinja2 import contextfilter
from jinja2 import Markup
from arrow import Arrow

from websauna.compat import typing
from websauna.utils import html
from websauna.utils import slug


@contextfilter
def uuid_to_slug(jinja_ctx, context, **kw):
    """Convert UUID object to a base64 encoded slug.

    Example:

    .. code-block:: html+jinja

        {% for question in latest_question_list %}
            <li>
              <a href="{{ route_url('details', question.uuid|uuid_to_slug) }}">
                {{ question.question_text }}
              </a>
            </li>
        {% endfor %}

    """
    return slug.uuid_to_slug(context)


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

    .. code-block:: html+jinja

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


    Then in your initialization:::

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
    include_filter(config, "uuid_to_slug", uuid_to_slug)
    include_filter(config, "friendly_time", friendly_time)
    include_filter(config, "datetime", filter_datetime)
    include_filter(config, "escape_js", escape_js)
    include_filter(config, "timestruct", timestruct)
    include_filter(config, "to_json", to_json)
    include_filter(config, "fromtimestamp", fromtimestamp)


