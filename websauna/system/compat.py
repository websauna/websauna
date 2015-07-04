"""Compatibility layer between different Python versions."""
import sys

if sys.version_info >= (3, 5):
    import typing
else:
    from backports import typing
