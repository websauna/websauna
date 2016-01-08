"""HTTP header helper utilities."""


# https://github.com/pypa/warehouse/blob/master/warehouse/cache/http.py
def add_vary_callback(*varies):
    def inner(request, response):
        vary = set(response.vary if response.vary is not None else [])
        vary |= set(varies)
        response.vary = vary
    return inner
