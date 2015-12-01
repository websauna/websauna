import os
from uuid import UUID

#: BBB Remove importers and move them to right place
from websauna.utils.time import now


def secure_uuid():
    """Create a non-conforming 128-bit random version 4 UUID.

    Random UUID is a RFC 4122 compliant UUID version 4 128-bit number. By default 6 fixed bits, 4 bits for version and 2 bits reserved for other purposes, are fixed. This function behaves like Python's ` uuid4()`` but also randomizes the remaining six bits, generating up to 128 bit randomness.

    This function also sources all bytes from `os.urandom()` to guarantee the randomness and security and does not rely operating system libraries.

    Using ``secure_uuid()`` poses a risk that generated UUIDs are not accepted when communicating with third party system. However, they are observed to be good for URLs and to be stored in PostgreSQL.

    More information

    * http://crypto.stackexchange.com/a/3525/25874

    * https://tools.ietf.org/html/rfc4122
    """
    return UUID(bytes=os.urandom(16), version=4)