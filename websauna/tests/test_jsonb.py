import unittest
import pytest
import datetime

import transaction

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy import engine_from_config
from websauna.system.model.meta import create_dbsession
from websauna.utils.jsonb import BadJSONData
from websauna.utils.jsonb import BadStoredData
from websauna.utils.jsonb import JSONBProperty
from websauna.utils.jsonb import ISO8601DatetimeConverter
from websauna.utils.jsonb import CannotProcessISO8601

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

    date_time_property = JSONBProperty("data", "/date_time_property", converter=ISO8601DatetimeConverter)


class DefautDataTestModel(Base):

    __tablename__ = "default_data_test_model"

    #: Running counter used in foreign key references
    id = Column(Integer, primary_key=True)

    #: Default value 1
    default_value_1 = JSONBProperty("data", "/default_value_1")

    #: Default value 2
    default_value_2 = JSONBProperty("data", "/default_value_2")

    data = Column(JSONB, default={"default_value_1": 1, "default_value_2": 2})


class TestJSON(unittest.TestCase):
    """JSONB fields and properties."""

    @pytest.fixture(autouse=True)
    def load_settings(self, ini_settings):
        self.settings = ini_settings

    def setUp(self):

        # Create a threadh-local automatic session factory
        self.session = create_dbsession(self.settings)
        self.engine = self.session.get_bind()

        # Load Bitcoin models to play around with
        with transaction.manager:
            Base.metadata.create_all(self.engine, tables=[TestModel.__table__, DefautDataTestModel.__table__])

    def tearDown(self):

        with transaction.manager:
            Base.metadata.drop_all(self.engine)

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

        with transaction.manager:
            val = 555

            model = TestModel()

            model.data = {"nested_dict": {}}
            model.nested_property = val

            self.session.add(model)

        with transaction.manager:
            model = self.session.query(TestModel).get(1)
            self.assertEqual(model.nested_property, val)

    def test_write_empty_field(self):
        """Create new instace, do not set the field, see it comes back as empty dict.."""

        model = TestModel()
        with transaction.manager:
            self.session.add(model)


        with transaction.manager:
            model = self.session.query(TestModel).get(1)
            self.assertEqual(model.data, {})

    def test_persistent_null(self):
        """See that if we manage to slip NULL data to persistent object we get friendly error."""

        with transaction.manager:
            model = TestModel()
            self.session.add(model)

        with transaction.manager:

            model = self.session.query(TestModel).get(1)

            # Emulate broken data
            model.data = None

            with self.assertRaises(BadStoredData):
                model.nested_property = 1

    def test_datetime(self):
        """See that we serialize and deserialize datetimes correctly, including timezone info."""

        val = datetime.datetime.now(datetime.timezone.utc)

        with transaction.manager:
            model = TestModel()
            model.date_time_property = val
            self.session.add(model)

        with transaction.manager:
            model = self.session.query(TestModel).get(1)
            val2 = model.date_time_property

            self.assertEqual(val, val2)

    def test_datetime_none(self):
        """See that we serialize and deserialize None datetimes correctly."""

        val = None

        with transaction.manager:
            model = TestModel()
            model.date_time_property = val

            self.session.add(model)

        with transaction.manager:
            model = self.session.query(TestModel).get(1)

            val2 = model.date_time_property

            self.assertEqual(val, val2)

    def test_datetime_no_timezone(self):
        """Don't let naive datetimes slip through."""

        val = datetime.datetime.utcnow()

        model = TestModel()

        with self.assertRaises(CannotProcessISO8601):
            model.date_time_property = val

    def test_modify_non_flushed(self):
        """Modifying non-flushed database field correctly handles default values.

        Consider the following situation.

        We have a JSONB field with defaults::

            class Product:
                product_data = JSONB(default={"foo": "bar", price: None)}

        Then we construct a new instance and try to modify data before flush::

            p = Product()
            p.product_data["foo"] = 123

        -> this will invalidate the default value
        """

        with transaction.manager:
            model = DefautDataTestModel()
            model.default_value_1 = "xxx"
            assert model.data == {"default_value_1": "xxx", "default_value_2": 2}
            self.session.add(model)

        with transaction.manager:
            model = self.session.query(DefautDataTestModel).get(1)
            assert model
            assert model.default_value_2 == 2