"""Authomatic integration."""
import authomatic


_authomatic = None

# TODO: Change to registry based

def setup(authomatic_secret, config):
    global _authomatic
    _authomatic = authomatic.Authomatic(config=config, secret=authomatic_secret)


def get():
    return _authomatic
