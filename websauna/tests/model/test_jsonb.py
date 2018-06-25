"""JSONB field behavior checks."""
# Pyramid
import transaction

import pytest

# Websauna
from websauna.system.model.json import NestedMutationDict
from websauna.system.user.models import User
from websauna.tests.test_utils import create_user


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


test_data = (('xxx', 1), ('yyy', 0))


@pytest.mark.parametrize('query_param,expected_lines', test_data)
def test_query_jsonb_data(dbsession, registry, query_param, expected_lines):
    """Query JSONB field by one of its keys."""
    with transaction.manager:
        u = create_user(dbsession, registry)
        assert isinstance(u.user_data, NestedMutationDict)
        u.user_data['phone_number'] = 'xxx'

    users = dbsession.query(User).filter(
        User.user_data['phone_number'].astext == query_param
    ).all()
    assert len(users) == expected_lines
