"""Test utils.time."""
from datetime import datetime
from datetime import timezone

from websauna.utils import time


def test_now():
    """Test time.now."""
    func = time.now
    result = func()

    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc
