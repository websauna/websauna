from pyramid.events import BeforeRender
from websauna.system.admin.utils import get_admin


def includeme(config):

    def on_before_render(event):
        # Expose Admin object to templates
        request = event["request"]
        event["admin"] = get_admin(request)

    config.add_subscriber(on_before_render, BeforeRender)



