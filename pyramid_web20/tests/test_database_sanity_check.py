"""Tests for checking database sanity checks functions correctly."""

from pyramid_web20.system.model.sanitycheck import is_sane_database
from sqlalchemy import engine_from_config, Column, Integer
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


def setup_module(self):
    # Quiet log output for the tests
    import logging
    from pyramid_web20.system.model.sanitycheck import logger
    logger.setLevel(logging.FATAL)



class SaneTestModel(Base):
    """A sample SQLAlchemy model to demostrate db conflicts. """

    __tablename__ = "sanity_check_test"

    #: Running counter used in foreign key references
    id = Column(Integer, primary_key=True)


def test_sanity_pass(ini_settings, dbsession):
    """See database sanity check completes when tables and columns are created."""

    engine = engine_from_config(ini_settings, 'sqlalchemy.')
    conn = engine.connect()
    trans = conn.begin()

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        Base.metadata.drop_all(engine, tables=[SaneTestModel.__table__])
    except sqlalchemy.exc.NoSuchTableError:
        pass

    Base.metadata.create_all(engine, tables=[SaneTestModel.__table__])

    try:
        assert is_sane_database(Base, session) is True
    finally:
        Base.metadata.drop_all(engine)


def test_sanity_table_missing(ini_settings, dbsession):
    """See check fails when there is a missing table"""

    engine = engine_from_config(ini_settings, 'sqlalchemy.')
    conn = engine.connect()
    trans = conn.begin()

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        Base.metadata.drop_all(engine, tables=[SaneTestModel.__table__])
    except sqlalchemy.exc.NoSuchTableError:
        pass

    assert is_sane_database(Base, session) is False


def test_sanity_column_missing(ini_settings, dbsession):
    """See check fails when there is a missing table"""

    engine = engine_from_config(ini_settings, 'sqlalchemy.')
    conn = engine.connect()
    trans = conn.begin()

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        Base.metadata.drop_all(engine, tables=[SaneTestModel.__table__])
    except sqlalchemy.exc.NoSuchTableError:
        pass
    Base.metadata.create_all(engine, tables=[SaneTestModel.__table__])

    # Delete one of the columns
    engine.execute("ALTER TABLE sanity_check_test DROP COLUMN id")

    assert is_sane_database(Base, session) is False
