"""HTML manipulation helpers."""
# Standard Library
import typing as t


_js_escapes = {
    ord('\\'): '\\u005C',
    ord('\''): '\\u0027',
    ord('"'): '\\u0022',
    ord('>'): '\\u003E',
    ord('<'): '\\u003C',
    ord('&'): '\\u0026',
    ord('='): '\\u003D',
    ord('-'): '\\u002D',
    ord(';'): '\\u003B',
    ord('\u2028'): '\\u2028',
    ord('\u2029'): '\\u2029'
}

# Escape every ASCII character with a value less than 32.
_js_escapes.update((ord('%c' % z), '\\u%04X' % z) for z in range(32))


def escape_js(value: t.AnyStr) -> str:
    """Hex encodes characters for use in JavaScript strings.

    :param value: String to be escaped.
    :return: A string safe to be included inside a <script> tag.
    """
    return str(value).translate(_js_escapes)
