"""URL slug helpers."""
import uuid
import base64

def uuid_to_slug(uuid_):
    """Create a URL slug from UUID.

    Courtesy of MJ: # http://stackoverflow.com/a/12270917/315168
    """

    encoded = base64.b64encode(uuid_.bytes)
    import ipdb ; ipdb.set_trace()

    # URLs don't like +
    return encoded.decode("utf-8").rstrip('=\n').replace('/', '_').replace("+", "-")


def slug_to_uuid(slug):
    """Convert UUID URL slug to UUID object."""
    bytes = (slug + '==').replace('_', '/').replace("-", "+")
    bytes = base64.b64decode(bytes)
    return uuid.UUID(bytes=bytes)
