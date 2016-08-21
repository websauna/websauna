"""Transaction retry point support for command line applications and daemons.."""

import logging
import threading
from functools import wraps

import transaction


logger = logging.getLogger(__name__)


class NotRetryable(Exception):
    pass


class TransactionAlreadyInProcess(Exception):
    pass


def ensure_transactionless(msg=None):
    """Make sure the current thread doesn't already have db transaction in process."""

    if transaction.manager._txn:
        if not msg:
            msg = "Dangling transction open in transaction.manager. You should not start new one."

        transaction_thread = getattr(transaction.manager, "begin_thread", None)
        logger.fatal("Transaction state management error. Trying to start TX in thread %s. TX started in thread %s", threading.current_thread(), transaction_thread)

        raise TransactionAlreadyInProcess(msg)


def retryable(func):
    """Function decorator for§ SQL Serialized transaction conflict resolution through retries.

    """

    @wraps(func)
    def decorated_func(*args, **kwargs):

        # Make sure we don't re-enter to transaction
        ensure_transactionless()

        # Get how many attempts we want to do
        manager = transaction.manager
        retry_attempt_count = getattr(manager, "retry_attempt_count", None)
        if not retry_attempt_count:
            raise NotRetryable("TransactionManager is not configured with default retry attempt count")

        # Run attempt loop
        for num, attempt in enumerate(manager.attempts(retry_attempt_count)):
            if num >= 1:
                logger.info("Transaction retry attempt #%d for function %s", num + 1, func)
            with attempt:
                return func(*args, **kwargs)

    return decorated_func