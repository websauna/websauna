"""Default template variables."""

from pyramid.events import BeforeRender


# TODO: We expose this as a global for documentation. Migrate to non-global map in the future.
_template_variables = {}


def var(name):
    """Decorator to mark template variables for documentation."""

    def _inner(func):
        _template_variables[name] = func
        return func

    return _inner


@var("site_name")
def site_name(request, registry, settings):
    """Expose website name from ``websauna.site_name`` config variable to templates.

    Example:

    .. code-block:: html+jinja

        <div class="jumbotron text-center">
            <h1>{{ site_name }}</h1>
            <p class="lead text-center">
                {{ site_tag_line }}
            </p>
        </div>

    """
    return settings["websauna.site_name"]


@var("site_url")
def site_url(request, registry, settings):
    """Expose website URL from ``websauna.site_url`` config variable to templates.

    .. note ::

        You should not use this variable in web page templates. This variable is intended for cases where one needs templating without running a web server.

    The correct way to get the home URL of your website is:

    .. code-block:: html+jinja

        <a href="{{ request.route_url('home') }}">Home</a>

    """
    return settings["websauna.site_url"]


@var("site_author")
def site_author(request, registry, settings):
    """Expose website URL from ``websauna.site_author`` config variable to templates.

    This is used in footer to display the site owner.
    """
    return settings["websauna.site_author"]


@var("site_tag_line")
def site_tag_line(request, registry, settings):
    """Expose website URL from ``websauna.site_tag_line`` config variable to templates.

    This is used on the default front page to catch the attention of audience.
    """
    return settings["websauna.site_tag_line"]


@var("site_email_prefix")
def site_email_prefix(request, registry, settings):
    """Expose website URL from ``websauna.site_email_prefix`` config variable to templates.

    This is used as the subject prefix in outgoing email. E.g. if the value is ``SuperSite``you'll email subjects::

        [SuperSite] Welcome to www.supersite.com

    """
    return settings["websauna.site_email_prefix"]


@var("site_time_zone")
def site_time_zone(request, registry, settings):
    """Expose website URL from ``websauna.site_time_zone`` config variable to templates.

    By best practices, all dates and times should be stored in the database using :term:`UTC` time. This setting allows quickly convert dates and times to your local time.

    Example:

    .. code-block:: html+jinja

        <p>
            <strong>Bar opens</strong>:
            {{ opening_at|friendly_time(timezone=site_time_zone) }}
        </p>

    Default value is ``UTC``.

    See `timezone abbreviation list <https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations>`_.
    """
    return settings.get("websauna.site_timezone", "UTC")


@var("js_in_head")
def js_in_head(request, registry, settings):
    """Should ``<script>`` tags be placed in ``<head>`` or end of ``<body>``.

    """
    on_demand_resource_renderer = getattr(request, "on_demand_resource_renderer")
    if on_demand_resource_renderer and on_demand_resource_renderer.is_js_in_head(request):
        return True
    else:
        return False


@var("on_demand_resource_renderer")
def on_demand_resource_renderer(request, registry, settings):
    """Active instance of :py:class:`websauna.system.core.render.OnDemandResourceRenderer` managing dynamic CSS and JS. May be None."""
    on_demand_resource_renderer = getattr(request, "on_demand_resource_renderer")
    return on_demand_resource_renderer


def includeme(config):

    def on_before_render(event):
        # Augment Pyramid template renderers with these extra variables and deal with JS placement

        request = event["request"]

        for name, func in _template_variables.items():
            event[name] = func(request, request.registry, request.registry.settings)

    config.add_subscriber(on_before_render, BeforeRender)
