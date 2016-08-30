from sqlalchemy.orm import Session

from pyramid.interfaces import IRequest
from pyramid.registry import Registry
from pyramid.request import Request


def make_routable_request(dbsession: Session, registry: Registry, path="/") -> IRequest:
    """Creates a dummy request that has route_url and other routing methods.

    As this request does not get HTTP hostname and such stuff from WSGI environment, a configuration variable ``websauna.site_url`` is passed as the base URL.

    See also :func:`make_dummy_request`.
    """

    base_url = registry.get("websauna.site_url", None)

    # TODO: Honour request_factory here
    request = Request.blank(path, base_url=base_url)
    request.registry = registry
    request.user = None
    request.dbsession = dbsession
    return request
