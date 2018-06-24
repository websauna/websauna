"""Test utils.qualname."""
import pytest

# Websauna
from websauna.utils import html
from websauna.utils import qualname
from websauna.utils import slug
from websauna.utils import time


test_data = (
    (html.escape_js, 'websauna.utils.html.escape_js'),
    (qualname.get_qual_name, 'websauna.utils.qualname.get_qual_name'),
    (slug.slug_to_uuid, 'websauna.utils.slug.slug_to_uuid'),
    (slug.uuid_to_slug, 'websauna.utils.slug.uuid_to_slug'),
    (time.now, 'websauna.utils.time.now'),
)


@pytest.mark.parametrize('value,expected', test_data)
def test_get_qual_name(value, expected):
    """Test qualname.get_qual_name."""
    func = qualname.get_qual_name
    assert func(value) == expected
