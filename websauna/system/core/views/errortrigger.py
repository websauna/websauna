"""A test URL you can call to cause a production run time error."""
# Standard Library
import logging

# Pyramid
from pyramid.view import view_config

# Websauna
from websauna.system.core.loggingcapture import get_logging_user_context


logger = logging.getLogger(__name__)


@view_config(route_name='error_trigger')
def error_trigger(request):
    """An error logging view to generate a run-time error.
    """
    logger.debug("Logging debug message on debug level")
    logger.info("Logging debug message on info level")
    logger.warn("Logging debug message on warning level")
    user_context = get_logging_user_context(request)
    logger.error("Logging debug message on error level", exc_info=True, extra={"user": user_context})
    logger.fatal("Logging debug message on fatal level")

    raise RuntimeError("Test error.")
