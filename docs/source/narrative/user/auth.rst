==============
Authentication
==============

.. contents:: :local:

Introduction
============

Websuna uses session-based authentication on the default settings (:py:class:`websauna.system.auth.policy.SessionAuthenticationPolicy`). When a user logs in the logged in user id is stored in the session. All anonymous user ``request.session`` variables are carried over to logged in session.

Activating users
================

By default created user instances are not activated and thus cannot login. To activate user:

.. code-block:: python

        from websauna.utils.time import now
        from websauna.system.user.models import User
        from websauna.system.user.utils import get_user_registry

        def my_view(request):

            u = User(email="foobar@example.com")
            password = None  # Do not give password or give plain text entry here

            if password:
                # How to set a password on freshly created user
                user_registry = get_user_registry(request)
                user_registry.set_password(u, password)

            # Where did this user came to our site
            u.registration_source = "command_line"

            # Turn user activated
            u.activated_at = now()

            request.dbsession.add(u)

Authenticating user
===================

With username (email) and password
----------------------------------

See :py:meth:`websauna.system.user.loginservice.DefaultLoginService.check_credentials`.


Without password check
----------------------

See :py:meth:`websauna.system.user.loginservice.DefaultLoginService.authenticate_user`.

Invalidating session
====================

To protect against :term:`session fixation` attacks there exist :py:class:`websauna.system.user.events.UserAuthSensitiveOperation` event.

* Always fire this event when you change user authentication sensitive details (email, password)

* If you implement a custom session handling listen for this event and drop all user sessions on receiving it

Disabling default log in and sign up views
==========================================

pass
