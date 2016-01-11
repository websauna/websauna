==============
Authentication
==============

Websuna uses session-based authentication on the default settings (:py:class:`websauna.system.auth.policy.SessionAuthenticationPolicy`). When a user logs in the logged in user id is stored in the session. All anonymous user ``request.session`` variables are carried over to logged in session.

Invalidating session
====================

To protect against :term:`session fixation` attacks there exist :py:class:`websauna.system.user.events.UserAuthSensitiveOperation` event.

* Always fire this event when you change user authentication sensitive details (email, password)

* If you implement a custom session handling listen for this event and drop all user sessions on receiving it



