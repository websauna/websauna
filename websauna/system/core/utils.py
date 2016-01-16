from .interfaces import ISecrets


def get_secrets(registry) -> ISecrets:
    """Get the secrets provider dictionary."""
    return registry.getUtility(ISecrets)
