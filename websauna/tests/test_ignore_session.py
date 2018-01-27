"""Test ignore session function."""
import pytest

# Websauna
from websauna.system.core import session


test_data = (
    ('/home.html', False),
    ('/admin', False),
    ('/', False),
    ('/static/styles.css', True),
    ('/static/script.js', True),
    ('/static/image.gif', True),
    ('/static/image.jpg', True),
    ('/static/favicon.ico', True),
    ('/static/styles.CSS', True),
    ('/static/script.JS', True),
    ('/static/image.GIF', True),
    ('/static/image.JPG', True),
    ('/static/favicon.ICO', True),
    ('/notebook/static/styles.css', False),
    ('/notebook/static/script.js', False),
    ('/notebook/static/image.gif', False),
    ('/notebook/static/image.jpg', False),
    ('/notebook/static/favicon.ico', False),
)


@pytest.mark.parametrize('url,expected', test_data)
def test_ignore_session(url, expected):
    """Test ignore_session checking."""
    func = session.ignore_session
    assert func(url) is expected
