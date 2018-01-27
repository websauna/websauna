# Standard Library
import typing as t

# Pyramid
from pyramid.interfaces import IRequest
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.request import apply_request_extensions
from transaction import TransactionManager

# SQLAlchemy
from sqlalchemy.orm import Session

# Websauna
from websauna.system.model.meta import create_dbsession
from websauna.system.model.meta import create_transaction_manager_aware_dbsession  # noQA


def make_routable_request(dbsession: t.Optional[Session]=None, registry: t.Optional[Registry]=None, path='/') -> IRequest:
    """Creates a dummy request that has route_url and other routing methods.

    As this request does not get HTTP hostname and such stuff from WSGI environment, a configuration variable ``websauna.site_url`` is passed as the base URL.

    See also :func:`make_dummy_request`.

    TODO: Split this to two different functions: one for existing dbsession and one for where dbsession is connected.

    :param dbsession: Use existing dbsession or set to ``None`` to generate a new dbsession and transaction manager. None that this TM is not the thread local transaction manager in ``transaction.mananger``.
    :param registry: Configuration registry
    :param path: Path being requested.
    :return: Current request.
    """
    base_url = registry.settings.get("websauna.site_url", None)
    # TODO: Honour request_factory here
    request = Request.blank(path, base_url=base_url)
    request.registry = registry
    request.user = None
    request.view_name = ''

    # This will create request.tm, others
    apply_request_extensions(request)

    if dbsession:
        # Use the provided dbsession for this request
        request.dbsession = dbsession
        if hasattr(dbsession, "transaction_manager"):
            request.tm = request.transaction_manager = dbsession.transaction_manager
    else:
        # Create a new dbsession and transaction manager for this request
        tm = TransactionManager()
        dbsession = create_dbsession(request.registry, tm)
        request.dbsession = dbsession
        request.tm = request.transaction_manager = tm

        def terminate_session(request):
            # Close db session at the end of the request and return the db connection back to the pool
            dbsession.close()

        request.add_finished_callback(terminate_session)

    return request
