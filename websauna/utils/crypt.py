"""Cryptographic utilities."""

import string
import random


def generate_random_string(length: int, letters: str=string.ascii_lowercase + string.ascii_uppercase + string.digits) -> str:
    """Generate cryptographically safe random string.

    :param length: String length

    :param letters: Choose from this letter pool
    """
    return ''.join(random.SystemRandom().choice(letters) for _ in range(length))