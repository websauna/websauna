from pyramid_web20.system.admin import Admin


def test_model_admin_decoration():
    """See that user model admin registers correctly."""
    admin = Admin()

    # XXX: Make a test module. For now we reuse something we have.
    from pyramid_web20.system.user import admin as user_admin

    admin.scan(user_admin)
    assert len(admin.model_admins) > 0
