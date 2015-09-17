
class MergeError(Exception):
    pass


def merge(a: dict, b: dict) -> dict:
    """Merges b into a by deep copy and return merged result.

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen

    Courtesy of http://stackoverflow.com/a/15836901/315168
    """
    key = None

    try:
        if a is None or isinstance(a, str) or isinstance(a, int) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise MergeError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise MergeError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as e:
        raise MergeError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a


def combine(a, b):
    """Combines two dictionary and returns the result as a new dict.

    Keys in b override keys in a.
    """
    c = a.copy()
    merge(c, b)
    return c

def traverse(obj, visitor) -> object:
    """Traverse deeply-nested dict/list structure and mutate along the way..

    :param obj: dict/list to traverse
    :param visitor: callback(obj) -> obj called for every value member
    :return: Deep-copy of mutated data

    http://nvie.com/posts/modifying-deeply-nested-structures/
    """
    if isinstance(obj, dict):
        return {k: traverse(v, visitor) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [traverse(elem, visitor) for elem in obj]
    else:
        return visitor(obj)