=========================
Creating your first model
=========================

Now we have a working website in place. It's time to start add some content there.

In this tutorial chapter we'll create a :term:`model` for a blog post. The model describers what fields a blog post contains.

Adding a model
==============

Models are added to a ``models.py`` file which the ``websauna_app`` scaffold generated for you. Websauna uses :term`SQLAlchemy` for modelling.

Open ``models.py`` and add::

    from uuid import uuid4

    from sqlalchemy import Column, String, Integer, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from websauna.system.model.meta import Base
    from websauna.system.model.columns import UTCDateTime


    class Question(Base):

        #: The table in the database
        __tablename__ = "question"

        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)

        #: Publicly exposed non-guessable
        uuid = Column(UUID(as_uuid=True), default=uuid4)

        #: Question text
        question_text = Column(String(256), default=None)

        #: When this question was published
        published_at = Column(UTCDateTime, default=None)

        #: Relationship mapping between question and choice
        choices = relationship("Choice", back_populates="question", lazy="dynamic")


    class Choice(Base):

        #: The table in the database
        __tablename__ = "choice"

        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)

        #: Publicly exposed non-guessable id
        uuid = Column(UUID(as_uuid=True), default=uuid4)

        #: What the user sees for this choice
        choice_text = Column(String(256), default=None)

        #: How many times this choice has been voted
        votes = Column(Integer, default=0)

        #: Which question this choice is part of
        question_id = Column(Integer, ForeignKey('question.id'))
        question = relationship("Question", back_populates="choices")


Some notes:

* :py:class:`websauna.system.model.meta.Base` is the default base class for :term:`model`

* We define an :term:`UUID` column for randomly generated ids. We never expose the database primary key ``id`` to the world, as it might give intel for malicious actors targetting your website.

* We store time in the database explicitly using :term:`UTC` timezone. This will save you from `many time ambiguity issues <http://ideas.kentico.com/forums/239189-kentico-product-ideas/suggestions/6825844-always-store-dates-times-in-utc-in-the-database>`_.

Creating a migration
====================

Having a Python code is not enough for a working model. You need to inform your database to create a corresponding structures. This is called :term:`migration`.

If you try to start your development server in this point the :term:`sanity check` feature aborts the start up::

    ws-pserve development.ini --reload

    ...
    Model <class 'myapp.models.Question'> declares table question which does not exist in database Engine(postgresql://localhost/myapp_dev)
    ...
    websauna.system.SanityCheckFailed: The database sanity check failed. Check log for details.
    ...

To create a migration script for your application run the following command in your application folder::

    ws-alembic -c development.ini revision --auto -m "Added choices and questions"

    ... a lot of output ...
    .. All done

.. note::

    Thumbs up! PostgreSQL migrations are transactional. The whole migration always goes through or none of it. All databases do not have this kind of safety making running a migration a risky operation.

You need to do this every time columns change. After the script is created on your local computer you can re-use it across the different computers where the application is installed (:term:`staging` server, :term:`production` server).

Then apply migration to your local database::

    ws-alembic -c development.ini upgrade head

    ... a lot of output ...
    .. All done

Exploring tables
================

Like earlier, you can pop up :ref:`ws-db-shell` command to see that new tables appeared in the database.

More information
================

See :doc:`models documentation <../narrative/modelling/models>`.