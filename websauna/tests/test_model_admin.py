from pyramid.config import Configurator

from websauna.system.admin.admin import Admin


def test_model_admin_decoration():
    """See that user model admin registers correctly."""
    admin = Admin()

    # XXX: Make a test module. For now we reuse something we have.
    from websauna.system.user import admin as user_admin

    config = Configurator(settings={})

    admin.scan(config, user_admin)
    assert len(admin.model_admins) > 0
