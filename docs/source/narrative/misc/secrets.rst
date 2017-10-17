.. _secrets:

=======
Secrets
=======

.. contents:: :local:

Introduction
============

Secret files are configuration files which contain sensitive material. Additional measurements must be taken that this material is not leaked. For example protection measurements include

* Secrets files are not in the version control.

* Secrets files are in version control, but encrypted and reading requires a decryption key. This is so called vault approach.

* Secrets are not in files, but passed to the process externally, e.g. in operating system environment variables.

Using secrets in your application
=================================

Example how to store Facebook app access token securely.

.. code-block:: python

    def get_opengraph_access_token(request: Request) -> str:
        """Get FB access_token needed to access OpenGraph API."""

        # Get access to INI secrets read during app start up
        secrets = get_secrets(request.registry)

        token = secrets.get("facebook_crawl.app_access_token")
        if not token:
            raise RuntimeError("secrets.ini [facebook_crawl] section invalid")

        return token


    def crawl_facebook(request, asset: Asset):
        count = 0
        dbsession = Session.object_session(asset)
        assert dbsession

        fb_link = asset.other_data.get("facebook")
        assert fb_link

        access_token = get_opengraph_access_token(request)

        # Convert FB page link to page id
        parts = urlparse(fb_link)
        resp = requests.get("https://graph.facebook.com/v2.7/", params={"id": fb_link, "access_token": access_token})

        if resp.status_code != 200:
            raise RuntimeError("Could not translate link to page id: {}".format(fb_link))

Then ``test-secrets.ini`` has:

.. code-block:: ini

    [facebook_crawl]
    # Obtained from https://developers.facebook.com/tools/accesstoken/
    app_access_token = xxxx

INI based secrets
=================

Websauna currently supports simple :term:`INI` based secrets.

* File is called either ``development-secrets.ini``, ``test-secrets.ini`` or ``production-secrets.ini``.

* The default :term:`scaffold` makes sure this file is in :term:`.gitignore`, so that it does not end up in version control.

* The main application configuration file (``development.ini``) refers to this file through :ref:`websauna.secrets_file` configuration variable.

* The secrets reading supports environment variable interpolation. This is useful for open continuous integration systems like Travis.

* Random tokens are randomized during the project generation by ``cookiecutter-websauna-app`` :term:`cookiecutter` template.

Example ``development-secrets.ini``::

    [authentication]
    # This is a secret seed used in email login
    secret = 3a704df1836cca928189726b4e692fe59ca41027

    [authomatic]
    # This is a secret seed used in various OAuth related keys
    secret = 936e70e21f1b94aa7aa5560bd6b3831c3a1da2ad

    # Get Facebook consumer key and consumer secret from http://developer.facebook.com/
    [facebook]
    class = authomatic.providers.oauth2.Facebook
    consumer_key = 8955434672XXXX
    consumer_secret = ef501136facXXXXXXXX
    scope = user_about_me, email
    mapper = websauna.system.user.social.FacebookMapper

    # Get Twitter consumer key and consumer secret from TODO
    [twitter]
    class = authomatic.providers.oauth1.Twitter
    consumer_key =
    consumer_secret =
    scope =
    mapper =

    # The secret used to hash session keys
    [session]
    secret = 646c5d0fe3eebd6d8ab9b41aeefd4658db7e477a

Using environment variables
---------------------------

You can also use environment variable interpolation::

    # Read environment variables from os.environ
    [facebook]
    class = authomatic.providers.oauth2.Facebook
    consumer_key = $FACEBOOK_CONSUMER_KEY
    consumer_secret = $FACEBOOK_API_KEY
    scope = user_about_me, email
    mapper = websauna.system.user.social.FacebookMapper

Create a file ``setup-secrets`` with content::

    RANDOM_VALUE="xxx"
    FACEBOOK_CONSUMER_KEY="xxx"
    FACEBOOK_CONSUMER_SECRET="xxx"

    export RANDOM_VALUE
    export FACEBOOK_CONSUMER_KEY
    export FACEBOOK_CONSUMER_SECRET

Then soure it in your shell to import environment variables:

.. code-block:: sh

    source setup-secrets

Vault
=====

Vault based secrets do not exist yet, but is planned for future versions.

More information
================

* See :py:meth:`websauna.system.Initializer.read_secrets`

* See :py:mod:`websauna.utils.secrets`