"""Utilities to encode and decode UUID objects as URL parameters.

We provide UUID to Base64 encoded string and back coding.

.. note ::

    The internal implemtation is subject to change to more efficient encoding. It is not recommended to use these as persistent URLs.
"""

import uuid

import binascii

import base64

class SlugDecodeError(Exception):
    """Raised when you pass invalid b64 slug data."""


def uuid_to_slug(uuid_:uuid.UUID) -> str:
    """Create a URL slug from UUID.

    Courtesy of MJ: # http://stackoverflow.com/a/12270917/315168

    :param uuid_: UUID object
    """

    # Catch some common typing errors
    assert isinstance(uuid_, uuid.UUID)

    encoded = base64.b64encode(uuid_.bytes)

    # https://docs.python.org/2/library/base64.html#base64.urlsafe_b64encode

    # URLs don't like +
    return encoded.decode("utf-8").rstrip('=\n').replace('/', '_').replace("+", "-")


def slug_to_uuid(slug:str) -> str:
    """Convert UUID URL slug to UUID object.

    This method raises `ValueError` if slug cannot be converted to UUID:

    try:
        delivery_uuid = slug_to_uuid(serica_data["cartID"])
    except ValueError as e:
        return HTTPNotFound("UUId was not a well-formed base64 encoded slug")

    :param slug: Base64 string presentation of UUID

    :raise: SlugError if the is an issue to decode slug
    """

    assert type(slug) == str

    try:
        bytes = (slug + '==').replace('_', '/').replace("-", "+")
        bytes = base64.b64decode(bytes)
        return uuid.UUID(bytes=bytes)
    except (ValueError, binascii.Error) as e:
        raise SlugDecodeError("Cannot decode supposed B64 slug: {}".format(slug)) from e

