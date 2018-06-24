"""Test utils.time."""
# Standard Library
from datetime import datetime
from datetime import timezone

# Websauna
from websauna.utils import time


def test_now():
    """Test time.now."""
    func = time.now
    result = func()

    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc
