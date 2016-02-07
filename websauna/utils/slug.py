"""Utilities to encode and decode UUID objects as URL parameters.

We provide UUID to Base64 encoded string and back coding.

.. note ::

    The internal implementation is subject to change to more efficient encoding. It is not recommended to use these as persistent URLs.

More info about slugs

* http://stackoverflow.com/questions/427102/what-is-a-slug-in-django
"""

import uuid

import binascii

import base64

class SlugDecodeError(Exception):
    """Raised when you pass invalid b64 slug data."""


def uuid_to_slug(uuid_: uuid.UUID) -> str:
    """Create a URL slug from UUID.

    Courtesy of MJ: # http://stackoverflow.com/a/12270917/315168

    .. note ::

        Slugs are supposed to be human readable. We are stretching that definition here a bit.

    :param uuid_: UUID object
    """

    # Catch some common typing errors
    assert isinstance(uuid_, uuid.UUID)

    encoded = base64.b64encode(uuid_.bytes)

    # https://docs.python.org/2/library/base64.html#base64.urlsafe_b64encode

    # URLs don't like +
    return encoded.decode("utf-8").rstrip('=\n').replace('/', '_').replace("+", "-")


def slug_to_uuid(slug: str) -> str:
    """Convert UUID URL slug string to UUID object.

    This method raises `ValueError` if slug cannot be converted to UUID:

    .. code-block:: python

        try:
            # Is like 'I0p4RyoIQe-EQ1GU_QicoQ'
            delivery_uuid = slug_to_uuid(art_data["cartID"])
        except SlugDecodeError as e:
            return HTTPNotFound("UUID was not a well-formed base64 encoded slug") from e

    :param slug: Base64 string presentation of UUID

    :raise: SlugDecodeError if the is an issue to decode slug
    """

    assert type(slug) == str

    try:
        bytes = (slug + '==').replace('_', '/').replace("-", "+")
        bytes = base64.b64decode(bytes)
        return uuid.UUID(bytes=bytes)
    except (ValueError, binascii.Error) as e:
        raise SlugDecodeError("Cannot decode supposed B64 slug: {}".format(slug)) from e

