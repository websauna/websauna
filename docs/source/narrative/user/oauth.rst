================================
Federated authentication (Oauth)
================================

Internally Websauna uses :py:term:`Authomatic` framework to implement :term:`OAuth`.

OAuth consumer and API key are stored in :term:`secrets`.

Mapping external users to Websauna users
========================================

By default, Websauna uses the email field of OAuth provider to map the external user to Websauna users. It's convenient as if the user has the same email account in Facebook and Twitter the user can use both service to sign in to Websauna and they get into the user account. Furthermore if the user does a Forget password action they will get a traditional email and password login.

In some cases mapping users by email is not desirable. For example, you don't trust the identity providers to do a good job with email confirmations. In this case you case customize the behavior by rolling out your own federated authentication account mapper.

See :py:class:`websauna.system.social.SocialLoginMapper` for more details.