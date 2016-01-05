========================
User, log in and sign up
========================

Websauna has a subsystem for user management.

* Pyramid authentication is used for authenticating users

* Default SQLAlchemy models are provided for users and groups through Horus

* Default Bootstrap templates for log in, sign up and other related forms are available

* Authomatic is used for social logins: Facebook, Twitter, Github and other OAuth-based systems


Advanced
========

Generating test users
---------------------

Below is a simple shell script to generate empty users for manual testing purposes::

    from websauna.system.user.utils import get_user_class

    # Get instance of whatever user class is configured for Websauna
    User = get_user_class(registry)

    for i in range(0, 100):
        username = "u{}".format(i)
        email = "dummy{}@example.com".format(i)
        password = "x"
        user = User(username=username, email=email, password=password)
        user.user_registration_source = User.USER_MEDIA_DUMMY
        DBSession.add(user)

    transaction.commit()


Getting all users who are members of a group
--------------------------------------------

Example::

    admin_group = DBSession.query(Group).filter_by(name="admin").first()
    users = admin_group.users