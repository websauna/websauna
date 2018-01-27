"""Cryptographic utilities."""
# Standard Library
import random
import string


_default = string.ascii_lowercase + string.ascii_uppercase + string.digits


def generate_random_string(length: int, letters: str=_default) -> str:
    """Generate cryptographically safe random string.

    :param length: String length
    :param letters: Choose from this letter pool
    """
    return ''.join(random.SystemRandom().choice(letters) for _ in range(length))
