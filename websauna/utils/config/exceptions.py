"""Exceptions."""


class WebsaunaConfigException(Exception):
    """Websauna config exception base class."""

    pass


class InvalidResourceScheme(WebsaunaConfigException):
    """Include reference does not exist."""

    pass


class NonExistingInclude(WebsaunaConfigException):
    """Include reference does not exist."""

    pass
