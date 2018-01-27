"""JSONB field behavior checks."""
# Pyramid
import transaction

# Websauna
from websauna.system.model.json import NestedMutationDict
from websauna.system.user.models import User
from websauna.tests.utils import create_user


def test_pending_jsonb_dict_new_key(dbsession, registry):
    """Check that new keys added to JSONB that is not committed yet are persistent."""

    with transaction.manager:
        u = create_user(dbsession, registry)
        assert isinstance(u.user_data, NestedMutationDict)
        u.user_data["phone_number"] = "xxx"

    with transaction.manager:
        u = dbsession.query(User).first()
        assert u.user_data.get("phone_number") == "xxx"


def test_committed_jsonb_dict_new_key(dbsession, registry):
    """Check that new keys added to JSONB dict that is loaded from db are persistent."""

    with transaction.manager:
        u = create_user(dbsession, registry)
        print(u.user_data)

    with transaction.manager:
        u = dbsession.query(User).first()
        assert isinstance(u.user_data, NestedMutationDict)
        u.user_data["phone_number"] = "xxx"

    with transaction.manager:
        u = dbsession.query(User).first()
        assert u.user_data.get("phone_number") == "xxx"
