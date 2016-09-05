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


def ensure_transactionless(msg=None, transaction_manager=transaction.manager):
    """Make sure the current thread doesn't already have db transaction in process.

    :param transaction_manager: TransactionManager to check. Defaults to thread local transaction manager.
    """

    txn = transaction_manager._txn
    if txn:
        if not msg:
            msg = "Dangling transction open in transaction.manager. You should not start new one."

        transaction_thread = getattr(transaction.manager, "begin_thread", None)
        logger.fatal("Transaction state management error. Trying to start TX in thread %s. TX started in thread %s", threading.current_thread(), transaction_thread)

        raise TransactionAlreadyInProcess(msg)


def retryable(tm=None, get_tm=None):
    """Function decorator for§ SQL Serialized transaction conflict resolution through retries.

    You need to give either ``tm`` or ``get_tm`` argument.

    Example:

    .. code-block:: python

        from websauna.system.model.retry import retryable

        def deposit_eth(web3: Web3, dbsession: Session, opid: UUID):

            @retryable(tm=dbsession.transaction_manager)
            def perform_tx():
                op = dbsession.query(CryptoOperation).get(opid)
                op.mark_performed()
                op.mark_broadcasted()
                # Transaction confirmation count updater will make sure we have enough blocks,
                # and then will call mark_completed()

        perform_tx()

    Example using class based transaction manager resolver:

    .. code-block:: python

        from websauna.system.model.retry import retryable

        class OperationQueueManager:

            def __init__(self, web3: Web3, dbsession: Session, asset_network_id, registry: Registry):
                assert isinstance(registry, Registry)
                assert isinstance(asset_network_id, UUID)
                self.web3 = web3
                self.dbsession = dbsession
                self.asset_network_id = asset_network_id
                self.registry = registry
                self.tm = self.dbsession.transaction_manager

            def _get_tm(*args, **kargs):
                self = args[0]
                return self.tm

            @retryable(get_tm=_get_tm)
            def get_waiting_operation_ids(self) -> List[Tuple[UUID, CryptoOperationType]]:
                wait_list = self.dbsession.query(CryptoOperation, CryptoOperation.id, CryptoOperation.state, CryptoOperation.operation_type).filter_by(network_id=self.asset_network_id, state=CryptoOperationState.waiting)

                # Flatten
                wait_list = [(o.id, o.operation_type) for o in wait_list]
                return wait_list

            def run_waiting_operations(self):
                # Performed inside TX retry boundary
                ops = self.get_waiting_operation_ids()

    :param tm: Transaction manager used to control the TX execution

    :param get_tm: Factory function that is called with *args and **kwargs to get the transaction manager
    """

    def _transaction_retry_wrapper(func):

        @wraps(func)
        def decorated_func(*args, **kwargs):

            if get_tm:
                manager = get_tm(*args, **kwargs)
            else:
                # Get how many attempts we want to do
                manager = tm

            assert manager, "No transaction manager available for retry"

            # Make sure we don't re-enter to transaction
            ensure_transactionless(transaction_manager=manager)

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

    return _transaction_retry_wrapper