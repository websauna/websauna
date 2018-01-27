# Pyramid
import transaction

# Websauna
from websauna.system.user.models import User


def test_user_subsystem(init, dbsession):
    """Load the default user models and see we create correponding tables right."""

    with transaction.manager:
        u = User(email="example@example.com")
        dbsession.add(u)

    with transaction.manager:
        u = dbsession.query(User).get(1)
        assert u.email == "example@example.com"
