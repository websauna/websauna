"""Admin interface events."""


class AdminConstruction:
    """Fired when admin interface is constructed for the request.

    Subscribers may contribute their own parts and traversing to admin UI.
    """

    def __init__(self, admin):
        self.admin = admin
