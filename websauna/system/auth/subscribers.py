"""Handle incoming user events."""
# Pyramid
from pyramid.events import subscriber

# Websauna
from websauna.system.user.events import UserAuthSensitiveOperation
from websauna.utils.time import now


@subscriber(UserAuthSensitiveOperation)
def user_auth_details_changes(event: UserAuthSensitiveOperation):
    """Default logic how to invalidate sessions on user auth detail changes.

    If you are using different session management model you can install a custom handle.

    :param event: Incoming event instance
    """
    user = event.user
    # Update the timestamp which session validation checks on every request
    user.last_auth_sensitive_operation_at = now()
