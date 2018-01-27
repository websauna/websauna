"""Python object fully qualified name resolving."""


def get_qual_name(func: object) -> str:
    """Reverse resolve full dotted name of a Python function.

    Courtesy of http://stackoverflow.com/a/13653312/315168
    """
    return func.__module__ + "." + func.__name__
