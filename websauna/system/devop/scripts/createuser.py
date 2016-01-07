"""ws-create-user script."""

import os
import sys

from websauna.system.devop.cmdline import init_websauna
from websauna.system.user.utils import get_user_class, get_site_creator
from websauna.utils.configincluder import \
    monkey_patch_paster_config_parser
import transaction

from pyramid.paster import (
    setup_logging,
    )

from websauna.utils.time import now


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <email> <password>\n'
          '(example: "%s development.ini mikko@example.com verysecret")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):

    monkey_patch_paster_config_parser()

    if len(argv) < 4:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)

    request = init_websauna(config_uri)

    User = get_user_class(request.registry)
    dbsession = request.dbsession

    with transaction.manager:
        u = User(email=argv[2], username=argv[2])
        u.password = argv[3]
        u.registration_source = "command_line"
        u.activated_at = now()
        dbsession.add(u)
        dbsession.flush()

        site_creator = get_site_creator(request.registry)
        site_creator.init_empty_site(dbsession, u)

        print("Created user #{}: {}, admin: {}".format(u.id, u.email, u.is_admin()))


if __name__ == "__main__":
    main()