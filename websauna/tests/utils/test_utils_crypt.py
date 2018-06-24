"""Test utils.crypt."""
# Standard Library
import string

import pytest

# Websauna
from websauna.utils import crypt


test_data = (
    (32, None, crypt._default),
    (32, crypt._default, crypt._default),
    (40, string.digits, string.digits),
)


@pytest.mark.parametrize('length,letters,pool', test_data)
def test_generate_random_string(length, letters, pool):
    """Test crypt.generate_random_string.

    Test if length and letters params are respected.
    """
    func = crypt.generate_random_string
    params = {
        'length': length,
    }
    if letters:
        params['letters'] = letters
    result = func(**params)
    assert len(result) == length
    assert len([c for c in result if c in pool]) == length
