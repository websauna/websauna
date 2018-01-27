"""Deform's resource_registry mechanism to allow widgets to include CSS and JS on the page."""
# Pyramid
from deform import Form
from deform.widget import ResourceRegistry as _ResourceRegistry

# Websauna
from websauna.system.form.interfaces import IFormResources
from websauna.system.http import Request


class ResourceRegistry(_ResourceRegistry):
    """A resource registry that maintains dynamically included CSS and JS files for the page.

     * During view processing, widgets and such can request that their helper JS and CSS is included on the page rendering

     * :py:class:`websauna.system.core.render.OnDemandResourceRenderer` maintains a state whether JS should go the end of ``<body>`` or ``<head>``

    The best practice is to place all JavxaScript files before the closing ``</body>`` tag, so that they do not block the the page rendering and decrease the page response time. However, out there exist a lot of badly written JavaScript code which does not honour this - they have ``<script>`` tags in the middle of ``<body>`` and even worse assume you have loaded dependencies, like jQuery, in the ``<head>``. Namely, Deform 2 form library does this.

    ``BodyRelocatableResourceRegistry`` contains the logic to determine if ``<script>`` tags should go to the end of the page (preferred) or to ``<head>`` (in case some javascript makes assumptions of this). If any widget requires resources assume JS must go to head.

    See also :py:attr`deform.widget.default_resources` which includes the list of default resources activated for any form on the page.

    More information

    * https://developers.google.com/speed/docs/insights/BlockingJS

    * https://developers.google.com/web/fundamentals/performance/critical-rendering-path/adding-interactivity-with-javascript#parser-blocking-vs-asynchronous-javascript
    """

    def __init__(self, request: Request):
        # Load default resoucres from configuration
        form_resources = request.registry.getUtility(IFormResources)
        self.registry = form_resources.get_default_resources().copy()

    def pull_in_resources(self, request: Request, form: Form):
        """Add resources CSS and JS resources from Deform form to a Websauna rendering loop."""
        on_demand_resource_renderer = request.on_demand_resource_renderer

        #: TODO: Support for absolute URLs and such

        for css_url in self.get_widget_css_urls(request, form):
            on_demand_resource_renderer.request_resource("css", css_url)

        for js_url in self.get_widget_js_urls(request, form):
            on_demand_resource_renderer.request_resource("js", js_url, js_requires_head=True)

    def get_widget_js_urls(self, request: Request, form: Form):
        """Generate JS and CSS tags for a widget.

        For demo purposes only - you might have something specific to your application here.

        See http://docs.pylonsproject.org/projects/deform/en/latest/widget.html#the-high-level-deform-field-get-widget-resources-method
        """
        resources = form.get_widget_resources()
        js_resources = resources['js']
        js_links = [request.static_url(r) for r in js_resources]
        return js_links

    def get_widget_css_urls(self, request: Request, form: Form):
        """Generate JS and CSS tags for a widget.

        For demo purposes only - you might have something specific to your application here.

        See http://docs.pylonsproject.org/projects/deform/en/latest/widget.html#the-high-level-deform-field-get-widget-resources-method
        """
        resources = form.get_widget_resources()
        css_resources = resources['css']
        css_links = [request.static_url(r) for r in css_resources]
        return css_links
