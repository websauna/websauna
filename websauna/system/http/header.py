"""HTTP header helper utilities."""


# https://github.com/pypa/warehouse/blob/master/warehouse/cache/http.py
def add_vary_callback_if_cookie(*varies):
    """Add vary: cookie header to all session responses.

    Prevent downstream web serves to accidentally cache session set-cookie reponses,
    potentially resulting to session leakage.
    """
    def inner(request, response):
        vary = set(response.vary if response.vary is not None else [])
        vary |= set(varies)
        response.vary = vary
    return inner
