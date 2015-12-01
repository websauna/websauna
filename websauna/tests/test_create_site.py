import transaction

from websauna.system.user.usermixin import check_empty_site_init


def test_virgin_init_admin(init, dbsession):
    """When the user logs in first time see we create admin group and permissions for it."""

    # Load user model
    User = init.user_models_module.User
    Group = init.user_models_module.Group
    assert User

    # from websauna.system.user.models import User

    with transaction.manager:
        u = User(username="example", email="example@example.com")
        dbsession.add(u)
        dbsession.flush()
        assert not u.is_admin()
        check_empty_site_init(dbsession, u)

    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert dbsession.query(Group).count() == 1
        assert u.is_admin()

