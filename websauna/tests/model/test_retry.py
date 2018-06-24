"""Test SQL transaction conflict resolution."""
# Standard Library
import threading
import time

# Pyramid
import transaction

# SQLAlchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Numeric

import pytest

# Websauna
from websauna.system.model.meta import Base
from websauna.system.model.meta import create_dbsession
from websauna.system.model.retry import CannotRetryAnymore
from websauna.system.model.retry import is_retryable
from websauna.system.model.retry import retryable


_test_model = None


def get_test_model():
    global _test_model
    if _test_model:
        return _test_model

    class TestModel(Base):
        """A sample SQLAlchemy model to demostrate db conflicts. """

        __tablename__ = "test_model"

        #: Running counter used in foreign key references
        id = Column(Integer, primary_key=True)

        #: The total balance of this wallet in the minimum unit of cryptocurrency
        #: NOTE: accuracy checked for Bitcoin only
        balance = Column(Numeric(21, 8))

    _test_model = TestModel
    return _test_model


class ConflictThread(threading.Thread):
    """Launch two of these and they should cause database conflict."""

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.failure = None
        threading.Thread.__init__(self)

    def run(self):

        txn = None

        try:

            dbsession = self.session_factory()

            txn = dbsession.transaction_manager.begin()
            TestModel = get_test_model()

            # Both threads modify the same wallet simultaneously
            w = dbsession.query(TestModel).get(1)
            w.balance += 1

            # Let the other session to start its own transaction
            time.sleep(1)
            dbsession.transaction_manager.commit()
        except Exception as e:
            self.failure = (txn, dbsession, e)


class ConflictResolverThread(threading.Thread):
    """Launch two of these and they should cause database conflict and then retryable resolves it."""

    def __init__(self, dbsession_factory):
        self.dbsession_factory = dbsession_factory
        self.failure = None
        threading.Thread.__init__(self)
        self.success_count = 0
        self.failure_count = 0
        self.retry_count = 0

    def run(self):

        dbsession = self.dbsession_factory()

        # Execute the conflict sensitive code inside a managed transaction
        @retryable(tm=dbsession.transaction_manager)
        def myfunc():

            TestModel = get_test_model()

            # Both threads modify the same wallet simultaneously
            w = dbsession.query(TestModel).get(1)
            w.balance += 1

            # Let the other session to start its own transaction
            time.sleep(1)

        try:
            myfunc()
            self.success_count += 1
        except Exception as e:
            self.failure = e
            self.failure_count += 1

        # See retryable()
        self.retry_count = dbsession.transaction_manager.latest_retry_count


@pytest.fixture
def test_instance(dbsession):

    TestModel = get_test_model()
    Base.metadata.create_all(tables=[TestModel.__table__], bind=dbsession.get_bind())

    with dbsession.transaction_manager:

        # Create an wallet with balance of 10
        w = dbsession.query(TestModel).get(1)
        if not w:
            w = TestModel()
            dbsession.add(w)

        w.balance = 10


@pytest.fixture
def dbsession_factory(test_request):

    def factory():
        dbsession = create_dbsession(test_request.registry, manager=None)
        # Retry each transaction max 1 times
        dbsession.transaction_manager.retry_attempt_count = 2
        return dbsession

    return factory


def test_sql_transaction_conflict(test_instance, dbsession_factory):
    """Run database to a transaction conflict and see what exception it spits out, and make sure we know this is the exception we expect."""

    t1 = ConflictThread(dbsession_factory)
    t2 = ConflictThread(dbsession_factory)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # Either thread spits out:
    # sqlalchemy.exc.OperationalError: (TransactionRollbackError) could not serialize access due to concurrent update
    #  'UPDATE btc_wallet SET updated_at=%(updated_at)s, balance=%(balance)s WHERE btc_wallet.id = %(btc_wallet_id)s' {'btc_wallet_id': 1, 'balance': Decimal('11.00000000'), 'updated_at': datetime.datetime(2014, 12, 18, 1, 53, 58, 583219)}
    failure = t1.failure or t2.failure or None
    assert failure is not None

    txn, dbsession, exc = failure
    error = exc

    assert txn.status == "Commit failed"
    assert is_retryable(txn, error) is True


def test_conflict_resolved(test_instance, dbsession_factory, dbsession):
    """Use conflict resolver to resolve conflict between two transactions and see code retry is correctly run."""

    TestModel = get_test_model()

    t1 = ConflictResolverThread(dbsession_factory)
    t2 = ConflictResolverThread(dbsession_factory)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # sqlalchemy.exc.OperationalError: (TransactionRollbackError) could not serialize access due to concurrent update
    #  'UPDATE btc_wallet SET updated_at=%(updated_at)s, balance=%(balance)s WHERE btc_wallet.id = %(btc_wallet_id)s' {'btc_wallet_id': 1, 'balance': Decimal('11.00000000'), 'updated_at': datetime.datetime(2014, 12, 18, 1, 53, 58, 583219)}
    failure = t1.failure or t2.failure or None
    assert failure is None  # Both threads pass

    # Check both increments came through
    with transaction.manager:
        w = dbsession.query(TestModel).get(1)
        assert w.balance == 12

    success = sum([t1.success_count, t2.success_count])
    retries = sum([t1.retry_count, t2.retry_count])
    errors = sum([t1.failure_count, t2.failure_count])

    assert success == 2
    assert retries == 1  # At least one thread needs to retry
    assert errors == 0


def test_conflict_some_other_exception(dbsession):
    """See that unknown exceptions are correctly reraised by managed_transaction."""

    @retryable(tm=dbsession.transaction_manager)
    def do_stuff():
        raise ValueError("Unknown exception")

    with pytest.raises(ValueError):
        do_stuff()


def test_give_up(test_instance, dbsession_factory, dbsession):
    """See that the conflict resolver gives up after using given number of attempts to replay transactions."""

    # The resolved has retry count of 1,
    # First t1 success, t2 and t3 clases
    # Then t2 success, t3 retries but is out of
    t1 = ConflictResolverThread(dbsession_factory)
    t2 = ConflictResolverThread(dbsession_factory)
    t3 = ConflictResolverThread(dbsession_factory)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    failure = t1.failure or t2.failure or t3.failure or None
    assert isinstance(failure, CannotRetryAnymore)

    success = sum([t1.success_count, t2.success_count, t3.success_count])
    retries = sum([t1.retry_count, t2.retry_count, t3.retry_count])
    errors = sum([t1.failure_count, t2.failure_count, t3.failure_count])

    assert success == 2
    assert retries == 2
    assert errors == 1

    # Check 2 increments came through
    TestModel = get_test_model()
    with transaction.manager:
        w = dbsession.query(TestModel).get(1)
        assert w.balance == 12
