"""HTTP header helper utilities."""

import functools

# https://github.com/pypa/warehouse/blob/master/warehouse/cache/http.py
def add_vary_callback(*varies):
    def inner(request, response):
        vary = set(response.vary if response.vary is not None else [])
        vary |= set(varies)
        response.vary = vary
    return inner


# https://github.com/pypa/warehouse/blob/master/warehouse/cache/http.py
def add_vary(*varies):
    def inner(view):
        @functools.wraps(view)
        def wrapped(context, request):
            request.add_response_callback(add_vary_callback(*varies))
            return view(context, request)
        return wrapped
    return inner