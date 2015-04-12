import unittest
import pytest
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy import engine_from_config

from pyramid_web20.models import DBSession
from pyramid_web20.utils.jsonb import BadJSONData
from pyramid_web20.utils.jsonb import BadStoredData
from pyramid_web20.utils.jsonb import JSONBProperty


from jsonpointer import JsonPointerException


Base = declarative_base()


class TestModel(Base):
    """A sample SQLAlchemy model to demostrate db conflicts. """

    __tablename__ = "test_model"

    #: Running counter used in foreign key references
    id = Column(Integer, primary_key=True)

    #: The total balance of this wallet in the minimum unit of cryptocurrency
    #: NOTE: accuracy checked for Bitcoin only
    data = Column(JSONB, default={})

    #: Flat JSON property
    flat_property = JSONBProperty("data", "/flat_property")

    #: Nested JSON propety
    nested_property = JSONBProperty("data", "/nested_dict/nested_property")


@pytest.mark.usefixtures("test_case_ini_settings")
class TestJSON(unittest.TestCase):
    """JSONB fields and properties."""

    def setUp(self):

        self.engine = engine_from_config(self.config, 'sqlalchemy.')

        # Create a threadh-local automatic session factory
        self.session = DBSession

        # Load Bitcoin models to play around with
        Base.metadata.create_all(self.engine, tables=[TestModel.__table__])

        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.session.configure(bind=self.connection)

    def tearDown(self):

        # We need to perform commit here to see that the actual database does not burp on our JSON input
        self.transaction.commit()

        transaction = self.connection.begin()
        Base.metadata.drop_all(self.engine)
        transaction.commit()

        self.connection.close()
        self.session.remove()

    def test_flat_property_int(self):
        """Set a flat JSON value."""
        model = TestModel()
        model.flat_property = 1
        self.session.add(model)

    def test_flat_property_datetime(self):
        """Set invalid JSON value."""
        model = TestModel()
        with self.assertRaises(BadJSONData):
            model.flat_property = datetime.datetime.now()

    def test_write_nested_value_path_missing(self):
        """Write a nested value where the parent dictionary is missing."""

        model = TestModel()
        with self.assertRaises(JsonPointerException):
            model.nested_property = 123

    def test_set_nested_not_dict(self):
        """Set nested value in a member which is not dict."""

        val = 555

        model = TestModel()

        model.data = {"nested_dict": 1}
        with self.assertRaises(JsonPointerException):
            model.nested_property = val

    def test_write_read_persistent_nested(self):
        """Set nested JSON value and read it back from the database."""

        val = 555

        model = TestModel()

        model.data = {"nested_dict": {}}
        model.nested_property = val

        self.session.add(model)
        self.transaction.commit()

        self.transaction = self.connection.begin()
        model = self.session.query(TestModel).get(1)

        self.assertEqual(model.nested_property, val)

    def test_write_empty_field(self):
        """Create new instace, do not set the field, see it comes back as empty dict.."""

        model = TestModel()
        self.session.add(model)
        self.transaction.commit()

        self.transaction = self.connection.begin()
        model = self.session.query(TestModel).get(1)

        self.assertEqual(model.data, {})

    def test_persistent_null(self):
        """See that if we manage to slip NULL data to persistent object we get friendly error."""

        model = TestModel()
        self.session.add(model)
        self.transaction.commit()

        self.transaction = self.connection.begin()
        model = self.session.query(TestModel).get(1)

        # Emulate broken data
        model.data = None

        with self.assertRaises(BadStoredData):
            model.nested_property = 1
