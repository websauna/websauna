"""URL slug helpers."""
import uuid
import base64

# https://docs.python.org/2/library/base64.html#base64.urlsafe_b64encode

def uuid_to_slug(uuid_):
    """Create a URL slug from UUID.

    Courtesy of MJ: # http://stackoverflow.com/a/12270917/315168

    :param uuid_: UUID object
    """

    encoded = base64.b64encode(uuid_.bytes)

    # URLs don't like +
    return encoded.decode("utf-8").rstrip('=\n').replace('/', '_').replace("+", "-")


def slug_to_uuid(slug):
    """Convert UUID URL slug to UUID object.

    This method raises `ValueError` if slug cannot be converted to UUID:

    try:
        delivery_uuid = slug_to_uuid(serica_data["cartID"])
    except ValueError as e:
        return HTTPNotFound("UUId was not a well-formed base64 encoded slug")

    :param slug: Base64 string presentation of UUID

    """
    bytes = (slug + '==').replace('_', '/').replace("-", "+")
    bytes = base64.b64decode(bytes)
    return uuid.UUID(bytes=bytes)

