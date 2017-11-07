"""ws-create-user script.

Create a new site user from command line.
"""
# Standard Library
import getpass
import os
import sys
import typing as t

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.devop.scripts import feedback_and_exit
from websauna.system.devop.scripts import get_config_uri
from websauna.system.user.events import UserCreated
from websauna.system.user.interfaces import IUserModel
from websauna.system.user.models import Group
from websauna.system.user.utils import get_user_class
from websauna.system.user.utils import get_user_registry
from websauna.utils.time import now


def usage_message(argv: t.List[str]):
    """Display usage message and exit.

    :param argv: Command line arguments.
    :raises sys.SystemExit:
    """
    cmd = os.path.basename(argv[0])
    msg = (
        'usage: {cmd} <config_uri> [password] [--admin]\n'
        '(example: "{cmd} ws://conf/production.ini mikko@example.com verysecret --admin")'
    ).format(cmd=cmd)
    feedback_and_exit(msg, status_code=1, display_border=False)


def create(
        request,
        username: str,
        email: str,
        password: t.Optional[str]=None,
        source: str='command_line',
        admin: bool=False
) -> IUserModel:
    """Create a new site user from command line.

    :param request:
    :param username: Username, usually an email.
    :param email: User's email.
    :param password: Password.
    :param source: Source of this user, in here, command_line.
    :param admin: Set this user to admin. The first user is always implicitly admin.
    :return: Newly created user.
    """
    User = get_user_class(request.registry)
    dbsession = request.dbsession
    u = dbsession.query(User).filter_by(email=email).first()
    if u is not None:
        return u

    u = User(email=email, username=username)
    dbsession.add(u)
    dbsession.flush()  # Make sure u.user_data is set

    if password:
        user_registry = get_user_registry(request)
        user_registry.set_password(u, password)

    u.registration_source = source
    u.activated_at = now()

    request.registry.notify(UserCreated(request, u))
    if admin:
        group = dbsession.query(Group).filter_by(name='admin').one_or_none()
        group.users.append(u)

    return u


def main(argv: t.List[str]=sys.argv):
    """Create a new site user from command line.

    :param argv: Command line arguments, second one needs to be the uri to a configuration file.
    :raises sys.SystemExit:
    """
    if len(argv) < 3:
        usage_message(argv)

    config_uri = get_config_uri(argv)

    request = init_websauna(config_uri)
    email = argv[2]
    is_admin = True if '--admin' in argv else False
    password = argv[3] if len(argv) >= 4 and argv[3] != '--admin' else ''

    if not password:
        password = getpass.getpass('Password:')
        password2 = getpass.getpass('Password (again):')
        if password != password2:
            feedback_and_exit('Passwords did not match', display_border=False)

    with request.tm:
        u = create(request, email=email, username=email, password=password, admin=is_admin)
        message = 'Created user #{id}: {email}, admin: {is_admin}'.format(
            id=u.id,
            email=u.email,
            is_admin=u.is_admin()
        )

    feedback_and_exit(message, status_code=None, display_border=True)


if __name__ == "__main__":
    main()
