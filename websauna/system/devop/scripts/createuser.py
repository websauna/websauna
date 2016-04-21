"""ws-create-user script."""
import getpass

import os
import sys

from websauna.system.devop.cmdline import init_websauna
from websauna.system.user.events import UserCreated
from websauna.system.user.interfaces import IPasswordHasher
from websauna.system.user.utils import get_user_class, get_site_creator, get_user_registry

import transaction

from websauna.utils.time import now


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <email> [password]\n'
          '(example: "%s development.ini mikko@example.com")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):

    if len(argv) < 3:
        usage(argv)

    config_uri = argv[1]
    request = init_websauna(config_uri)

    User = get_user_class(request.registry)
    dbsession = request.dbsession

    if len(argv) == 4:
        password = argv[3]
    else:
        password = getpass.getpass("Password:")
        password2 = getpass.getpass("Password (again):")

        if password != password2:
            sys.exit("Password did not match")

    with transaction.manager:

        u = User(email=argv[2], username=argv[2])

        if password:
            user_registry = get_user_registry(request)
            user_registry.set_password(u, password)

        u.registration_source = "command_line"
        u.activated_at = now()
        dbsession.add(u)
        dbsession.flush()

        request.registry.notify(UserCreated(request, u))

        print("Created user #{}: {}, admin: {}".format(u.id, u.email, u.is_admin()))


if __name__ == "__main__":
    main()