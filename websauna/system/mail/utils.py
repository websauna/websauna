from pyramid_mailer import IMailer


def get_mailer(registry):
    """Get the active mailer.
    :param registry:
    :return: IMailer
    """
    return registry.getUtility(IMailer)