"""Extra template variables."""

from pyramid.events import BeforeRender


def includeme(config):

    site_name = config.registry.settings["pyramid_web20.site_name"]
    site_url = config.registry.settings["pyramid_web20.site_url"]

    def on_before_render(event):
        # Augment Pyramid template renderers with these extra variables
        event['site_name'] = site_name
        event['site_url'] = site_url

    config.add_subscriber(on_before_render, BeforeRender)
