"""The default password hashing implementation using Argon 2.

Argon 2 is the winner algorithm of Password Hashing Competition 2012-2015.

More information

* https://github.com/hynek/argon2_cffi

* https://password-hashing.net/
"""

import argon2

from zope.interface import implementer

from websauna.system.user.interfaces import IPasswordHasher


@implementer(IPasswordHasher)
class Argon2Hasher:
    """The default password hashing implementation using Argon 2."""

    def __init__(self):
        self.hasher = argon2.PasswordHasher()

    def hash_password(self, plain_text):
        return self.hasher.hash(plain_text)

    def verify_password(self, hashed_password, plain_text):
        try:
            self.hasher.verify(hashed_password, plain_text)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
