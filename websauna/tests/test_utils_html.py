"""Test utils.html."""
import pytest

# Websauna
from websauna.utils import html


test_data = (
    ('{"foo": "bar"}', r'{\u0022foo\u0022: \u0022bar\u0022}'),
    ('{"foo": "=-<"}', r'{\u0022foo\u0022: \u0022\u003D\u002D\u003C\u0022}'),
)


@pytest.mark.parametrize('value,expected', test_data)
def test_escape_js(value, expected):
    """Test html.escape_js."""
    func = html.escape_js
    assert func(value) == expected
