===================
Database management
===================


Advanced
========

Accessing SQLAlchemy engine object
----------------------------------

    from pyramid_web20.system.model import DBSession
    engine = DBSession.get_bind()

Printing out table creation schames from command line
-----------------------------------------------------

This is sometimes useful for manual migrations.

In the shell::

    from sqlalchemy.schema import CreateTable
    from pyramid_web20.system.model import DBSession

    engine = DBSession.get_bind()
    model_class = Delivery

    table_sql = CreateTable(model_class.__table__).compile(engine)
    print(table_sql)


