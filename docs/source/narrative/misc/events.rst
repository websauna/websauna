======
Events
======

Websauna uses :term:`Pyramid`'s event mechanism to decouple logic between Python modules.

Firing events
=============

For each event kind, a new event class is created holding data related to the event. Create ``events.py`` in your application and place different events your application can fire there.

Example event::

    """Events fired by websauna.system.user package."""
    from websauna.system.http import Request
    from websauna.system.user.models import User


    class FirstLogin:
        """User logs in to the site for the first time.

        Fired upon

        * Social media login

        * After clicking email activation link
        """

        def __init__(self, request:Request, user:User):
            self.request = request
            self.user = user

Then you can fire the event using :py:meth:`pyramid.registry.Registry.notify`::

    if not user.last_login_at:
        e = events.FirstLogin(request, user)
        request.registry.notify(e)

Subscribing events
==================

Create ``subscribers.py`` in your application and place event handlers there.

Here is an example event subscriber::

    """Handle incoming user events."""
    from pyramid.events import subscriber
    from websauna.system.user.events import UserAuthSensitiveOperation
    from websauna.utils.time import now


    @subscriber(UserAuthSensitiveOperation)
    def user_auth_details_changes(event:UserAuthSensitiveOperation):
        """Default logic how to invalidate sessions on user auth detail changes.

        If you are using different session management model you can install a custom handle.

        :param event: Incoming event instance
        """

        user = event.user

        # Update the timestamp which session validation checks on every request
        user.last_auth_sensitive_operation_at = now()

You need to install your event handles by scanning your subscribers module in your app :term:`Initializer`::

        # Grab incoming auth details changed events
        from myapp import subscribers
        self.config.scan(subscribers)

Stock events
============

See

* :py:mod:`websauna.system.admin.events`

* :py:mod:`websauna.system.user.events`


More information
================

See `events in Pyramid documentation <http://docs.pylonsproject.org/docs/pyramid/en/latest/narr/events.html>`_.