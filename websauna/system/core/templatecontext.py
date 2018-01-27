"""Websauna template filters ."""
# Standard Library
import datetime
import json
import typing as t

# Pyramid
from jinja2 import Markup
from jinja2 import contextfilter
from pyramid.config import Configurator
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request

import arrow
from arrow import Arrow
from pytz import timezone

# Websauna
from websauna.system.admin.utils import get_admin_url_for_sqlalchemy_object
from websauna.system.core.panel import render_panel as _render_panel
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
def admin_url(jinja_ctx, model_instance, *elements, **kw):
    """Link to model in admin interface.

    Takes an :term:`SQLAlchemy` model instance as a filter argument and resolves its admin page. This requires that a model admin has been correctly registered for SQLAlchemy model.

    Example:

    .. code-block:: html+jinja

        {% if request.user and request.user.is_admin %}
            <li>
              <a class="btn btn-danger" href="{{ choice|admin_url("edit") }}">
                Edit in admin
              </a>
            </li>
        {% endif %}

    Another example:

    .. code-block:: html+jinja

        <li>
          <a class="btn btn-danger" href="{{ choice|admin_url }}">
            View in admin
          </a>
        </li>
    """
    request = jinja_ctx.get('request')
    if not request:
        raise RuntimeError("Not rendered with request")

    if elements:
        view_name = elements[0]
    else:
        view_name = None

    link = get_admin_url_for_sqlalchemy_object(request.admin, model_instance, view_name=view_name)
    return link


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
def arrow_format(jinja_ctx, context, *args, **kw):
    """Format datetime using Arrow formatter string.

    Context must be a time/datetime object.

    :term:`Arrow` is a Python helper library for parsing and formatting datetimes.

    Example:

    .. code-block:: html+jinja

        <li>
          Offer created at {{ offer.created_at|arrow_format('YYYYMMDDHHMMss') }}
        </li>

    `See Arrow formatting <http://crsmithdev.com/arrow/>`__.
    """
    assert len(args) == 1, "We take exactly one formatter argument, got {}".format(args)
    assert isinstance(context, (datetime.datetime, datetime.time)), "Got context {}".format(context)
    a = arrow.get(context)
    return a.format(fmt=args[0])


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

    # Make relative time between two timestamps
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

    Example:

    .. code-block:: html+jinja

            {#
              Export server side generated graph data points
              to Rickshaw client side graph rendering
            #}
            {% if graph_data %}
              <script>
                window.graphDataJSON = "{{ graph_data|to_json }}";
              </script>
            {% endif %}

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
def render_panel(jinja_ctx, context, name, **kwargs):
    """Render a panel inline in a template.

    Allows placing :ref:`admin panels <admin-panel>` in templates directly.

    Example how to include panel at the top of admin CRUD listing template:

    .. code-block:: html+jinja

        {% block title %}

          <h1>{{title}}</h1>

          {{ context|render_panel(name="admin_panel", controls=False) }}

        {% endblock %}

    :param context: Any resource object, like ModelAdmin instance

    :param name: registered panel name, like ``admin_panel``

    :param kwargs: Passed to the panel function as is

    :return: HTML string of the rendered panel
    """
    request = jinja_ctx.get('request') or get_current_request()
    return _render_panel(context, request, name="admin_panel", **kwargs)


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
def from_timestamp(jinja_ctx, context, **kw):
    """Convert UNIX datetime to timestamp.

    Example:

    .. code-block:: html+jinja

        <p>
            Prestodoctor license expires: {{ prestodoctor.recommendation.expires|from_timestamp(timezone="US/Pacific")|friendly_time }}
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


def include_filter(config: Configurator, name: str, func: t.Callable, renderers=(".html", ".txt",)):
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
    include_filter(config, "from_timestamp", from_timestamp)
    include_filter(config, "arrow_format", arrow_format)
    include_filter(config, "render_panel", render_panel)
    include_filter(config, "admin_url", admin_url)
