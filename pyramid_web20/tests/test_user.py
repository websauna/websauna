import transaction


def test_user_subsystem(init, dbsession):
    """Load the default user models and see we create correponding tables right."""

    # Load user model
    User = init.user_models_module.User
    assert User

    with transaction.manager:
        u = User(email="example@example.com")
        dbsession.add(u)

    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert u.email == "example@example.com"
