"""Typing support for Websauna."""
# flake8: noqa
# Standard Library
from posix import stat_result as stat_result
from typing import *  # pragma: no cover


class DirEntry(Generic[AnyStr]):  # noqa: F405
    # This is what the scandir interator yields
    # The constructor is hidden

    name = ''
    path = ''

    def inode(self) -> int: ...  # noqa: E704

    def is_dir(self, follow_symlinks: bool = ...) -> bool: ...  # noqa: E704

    def is_file(self, follow_symlinks: bool = ...) -> bool: ...  # noqa: E704

    def is_symlink(self) -> bool: ...  # noqa: E704

    def stat(self) -> stat_result: ...  # noqa: E704
