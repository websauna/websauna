"""Register UserEvent subscribers."""
# Pyramid
from pyramid.events import subscriber

# Websauna
from websauna.system.user.events import UserCreated
from websauna.system.user.utils import get_site_creator


@subscriber(UserCreated)
def site_init(e: UserCreated):
    """Initialize the website.

    When the first user hits the site, capture its login and add him to the admin group.

    :param e: UserCreated event.
    """
    request = e.request
    user = e.user
    site_creator = get_site_creator(request.registry)
    site_creator.check_empty_site_init(request.dbsession, user)
