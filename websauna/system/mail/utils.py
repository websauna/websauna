# Pyramid
from pyramid.registry import Registry
from pyramid.util import DottedNameResolver

from pyramid_mailer import IMailer


def get_mailer(registry) -> IMailer:
    """Get the active mailer.
    :param registry:
    :return: IMailer
    """
    return registry.getUtility(IMailer)


def create_mailer(registry: Registry) -> IMailer:
    """Create a new mailer instance.

    """

    settings = registry.settings

    # Empty values are not handled gracefully, so mutate them here before passing forward to mailer
    if settings.get("mail.username", "x") == "":
        settings["mail.username"] = None

    if settings.get("mail.password", "x") == "":
        settings["mail.password"] = None

    mailer_class = settings.get("websauna.mailer", "")
    if mailer_class in ("mail", ""):
        # TODO: Make mailer_class explicit so we can dynamically load pyramid_mail.Mailer
        # Default
        from pyramid_mailer import mailer_factory_from_settings
        mailer = mailer_factory_from_settings(settings)
    else:
        # debug backend
        resolver = DottedNameResolver()
        mailer_cls = resolver.resolve(mailer_class)
        mailer = mailer_cls()

    return mailer
