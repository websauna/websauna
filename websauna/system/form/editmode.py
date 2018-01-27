"""Describe different form edit modes."""

# Standard Library
from enum import Enum


class EditMode(Enum):
    """Different edit modes for where a form can be."""

    #: Generate form for viewing contents (read-only)
    show = 0

    #: Generated form for creating a new object
    add = 1

    #: Generated form for editing an existing object
    edit = 2
