import io
import os
from pyramid.threadlocal import get_current_registry
from websauna.system import get_init
from websauna.system.core.secrets import get_secrets
from websauna.system.devop.backup import backup_site
from pyramid import testing

from tempfile import NamedTemporaryFile


def test_backup(dbsession, ini_settings):
    """Execute backup script with having our settings content."""

    f = NamedTemporaryFile(delete=False)
    temp_fname = f.name
    f.close()

    ini_settings["websauna.backup_script"] = "websauna.tests:backup_script.bash"
    ini_settings["backup_test.filename"] = temp_fname

    # Manually calling init would mess global dbsession management
    dbsession.remove()

    init = get_init(dict(__file__=ini_settings["_ini_file"]), ini_settings)
    init.run(ini_settings)

    testing.setUp(registry=init.config.registry)

    # Check we have faux AWS variable to export
    secrets = get_secrets(get_current_registry())
    assert "aws.access_key_id" in secrets

    try:

        # This will run the bash script above
        backup_site()

        # The result should be generated here
        assert os.path.exists(temp_fname)
        contents = io.open(temp_fname).read()

        # test-secrets.ini, AWS access key
        assert contents.strip() == "foo"
    finally:
        testing.tearDown()






