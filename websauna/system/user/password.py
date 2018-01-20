"""The default password hashing implementation using Argon 2.

Argon 2 is the winner algorithm of Password Hashing Competition 2012-2015.

More information

* https://github.com/hynek/argon2_cffi

* https://password-hashing.net/
"""
# Pyramid
from zope.interface import implementer

import argon2

# Websauna
from websauna.system.user.interfaces import IPasswordHasher


@implementer(IPasswordHasher)
class Argon2Hasher:
    """The default password hashing implementation using Argon 2."""

    def __init__(self):
        """Initialize Argon2Hasher."""
        self.hasher = argon2.PasswordHasher()

    def hash_password(self, plain_text: str) -> str:
        """Hash plain text password.

        :param plain_text: Password.
        :return: Hash of the password.
        """
        return self.hasher.hash(plain_text)

    def verify_password(self, hashed_password: str, plain_text: str) -> bool:
        """Validate if given hash and password match.

        :param hashed_password: Password hash.
        :param plain_text: Plain text password
        :return: Boolean indicating if plain_text relates to hashed_password.
        """
        try:
            self.hasher.verify(hashed_password, plain_text)
            verification = True
        except argon2.exceptions.VerifyMismatchError:
            verification = False
        return verification
