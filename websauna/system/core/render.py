"""Rendering helpers."""
# Websauna
from websauna.utils.orderedset import OrderedSet


class OnDemandResourceRenderer:
    """A JS and CSS resource registry which helps to allow widgets and such add JS and CSS files dynamically on the page.

    Usually instance of this class is available as ``request.on_demand_resource_renderer``.

    The best practice is to place all JavaScript files before the closing ``</body>`` tag, so that they do not block the the page rendering and decrease the page response time. However, out there exist a lot of badly written JavaScript code which does not honour this - they have ``<script>`` tags in the middle of ``<body>`` and even worse assume you have loaded dependencies, like jQuery, in the ``<head>``. Namely, Deform 2 form library does this.

    ``BodyRelocatableResourceRegistry`` contains the logic to determine if ``<script>`` tags should go to the end of the page (preferred) or to ``<head>`` (in case some javascript makes assumptions of this). If any widget requires resources assume JS must go to head.

    See also :py:attr`deform.widget.default_resources` which includes the list of default resources activated for any form on the page.

    More information

    * https://developers.google.com/speed/docs/insights/BlockingJS

    * https://developers.google.com/web/fundamentals/performance/critical-rendering-path/adding-interactivity-with-javascript#parser-blocking-vs-asynchronous-javascript
    """

    def __init__(self):
        self.resources = {
            "js": OrderedSet(),
            "css": OrderedSet(),
        }
        self.js_requires_head = False

    def request_resource(self, kind: str, resource_url: str, js_requires_head: bool=False):
        """A widget or something wants to place a CSS or JS file on the page rendering.

        :param kind: "js" or "css"
        :param resource_path: Resolved full URL to this resource
        :param js_requires_head: Move all JavaScript to <head> instead of </body> end. I.e. you have <script> tags in the middle of HTML.
        """
        self.resources[kind].add(resource_url)

        # If one JS wants to go head then everybody goes
        self.js_requires_head |= js_requires_head

    def is_js_in_head(self, request) -> bool:
        return self.js_requires_head

    def get_resources(self, kind) -> OrderedSet:
        """Get list of resource URLs to render.

        :param kind: "js" or "css"
        """
        return self.resources[kind]


def get_on_demand_resource_renderer(request):
    """Reify method for configuration."""
    return OnDemandResourceRenderer()
