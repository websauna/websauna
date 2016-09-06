from .interfaces import ISecrets


def get_secrets(registry) -> dict:
    """Get the secrets provider dictionary.

    :return: A dictionary containing secrets having {ini sectionid}.{key} as keys.
    """
    return registry.getUtility(ISecrets)
