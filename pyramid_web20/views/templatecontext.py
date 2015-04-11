"""Extra template variables."""

from pyramid.events import BeforeRender


def includeme(config):

    site_name = config.registry.settings["pyramid_web20.site_name"]
    site_url = config.registry.settings["pyramid_web20.site_url"]
    site_author = config.registry.settings["pyramid_web20.site_author"]
    site_tag_line = config.registry.settings["pyramid_web20.site_tag_line"]

    def on_before_render(event):
        # Augment Pyramid template renderers with these extra variables
        event['site_name'] = site_name
        event['site_url'] = site_url
        event['site_author'] = site_author
        event['site_tag_line'] = site_tag_line

    config.add_subscriber(on_before_render, BeforeRender)
