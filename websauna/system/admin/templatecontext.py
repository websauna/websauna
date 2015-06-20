from pyramid.events import BeforeRender
from websauna.system.admin import Admin


def includeme(config):

    def on_before_render(event):
        # Expose Admin object to templates
        request = event["request"]
        event["admin"] = Admin.get_admin(request.registry)

    config.add_subscriber(on_before_render, BeforeRender)



