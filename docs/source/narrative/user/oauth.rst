================================
Federated authentication (Oauth)
================================

Internally Websauna uses :py:term:`Authomatic` framework to implement :term:`OAuth`.

See Getting started tutorial how to set up Facebook authentication. Same mechanism applies to every OAuth provider like Google, Twitter and Github.

OAuth login service
===================

The default OAuth login logic is implemented in :py:class:`websauna.system.user.oauthloginservice.DefaultOAuthLoginService`. It directly wraps underlying :py:term:`Authomatic` request processing.

You can drop in your own replacement for OAuth authentication by overriding :py:meth:`websauna.system.Initializer.configure_federated_login`.

Mapping external users to Websauna users
========================================

By default, Websauna uses the email field of OAuth provider to map the external user to Websauna users. It's convenient as if the user has the same email account in Facebook and Twitter the user can use both service to sign in to Websauna and they get into the user account. Furthermore if the user does a Forget password action they will get a traditional email and password login.

In some cases mapping users by email is not desirable. For example, you don't trust the identity providers to do a good job with email confirmations. In this case you case customize the behavior by rolling out your own federated authentication account mapper.

See :py:class:`websauna.system.social.SocialLoginMapper` for more details.