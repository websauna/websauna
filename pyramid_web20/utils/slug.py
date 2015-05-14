import uuid


def uuid_to_slug(uuid_):
    """Create a URL slug from UUID.

    Courtesy of MJ: # http://stackoverflow.com/a/12270917/315168
    """
    return uuid_.bytes.encode('base64').rstrip('=\n').replace('/', '-')


def slug_to_uuid(slug):
    """Convert UUID URL slug to UUID object."""
    return uuid.UUID(bytes=(slug + '==').replace('-', '/').decode('base64'))