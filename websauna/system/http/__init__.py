from pyramid.request import Request as _Request


class Request(_Request):
    """HTTP request class.

    This is a Pyramid Request object augmented with type hinting information for Websauna-specific functionality.

    Counter-intuevily this request is also available in non-HTTP applications like command line applications and timed tasks. These applications do not get request URL from a front end HTTP webserver, but a faux request is constructed pointing to the website URL taken from ``websauna.site_url`` setting. This is to allow similar design patterns and methodology to be applied in HTTP and non-HTTP applications.
    """