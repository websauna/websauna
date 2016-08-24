=============================
Adding data and model methods
=============================

Now we have the model declared, but we do not yet have an user interface to manipulate questions and choices. However, we can do it from the shell.

In this tutorial chapter we show how to work with the :term:`notebook` on the database.

Enter the notebook shell
========================

Like earlier, we can start :term:`notebook`. This time we should see our model in the default variable list:

.. image:: images/question_model.png
    :width: 640px


Playing with the model API
==========================

Once you are in the shell, explore the model :term:`SQLAlchemy` API:

.. note ::

    You can use TAB key for autocompleting variable names in IPython Notebook. Just type few letters and hit tab and notebook will fill it for you.

.. code-block:: pycon

    # No questions are in the system yet.
    >>> dbsession.query(Question).all()
    []

    # Create a new Question.
    # Use websauna.utils.time.now() for filling in datetime.
    # websauna.utils.time.now() gives a timezone-enabled, UTC, datetime
    >>> from websauna.utils.time import now
    >>> q = Question(question_text="What's new?", published_at=now())

    # Add the object to the session save chain
    >>> dbsession.add(q)

    # The default attribute do not appear on the model instance
    # until you flush it to the database. The id value is still empty.
    >>> q.id

    # Let's flush and our id appears.
    >>> dbsession.flush()
    >>> q.id
    1

    # When the database transaction is committed, all the information
    # is permanently recorded to the database. Note that you need to call
    # transaction.commit() manually only in shell - the web code
    # will automatically commit the transaction after each successful HTTP
    # request.
    >>> transaction.commit()

    # Now try to access model field values via Python attributes:
    >>> q.question_text
    DetachedInstanceError                     Traceback (most recent call last)
    <ipython-input-9-555cab93d97c> in <module>()
    ----> 1 q.question_text
    [...]
        608             "Instance %s is not bound to a Session; "
        609             "attribute refresh operation cannot proceed" %
    --> 610             (state_str(state)))
        611
        612     has_key = bool(state.key)

    DetachedInstanceError: Instance <Question at 0x10b10a828> is not bound to a Session; attribute refresh operation cannot proceed

    # What happened? Well, due to SQLAlchemy's implementation, an instance cannot survive a transaction.
    # The solution (or workaround) is to re-fetch the instance, i.e. like so:
    >>> q = dbsession.query(Question).get(1)
    >>> q.question_text

    # Now we can access the object again:
    "What's new?"

    >>> q.pubished_at
    datetime.datetime(2016, 1, 11, 16, 4, 50, 30434, tzinfo=datetime.timezone.utc)

    # We can also explore random UUID
    >>> q.uuid
    UUID('d7a077b4-2f3a-4c34-aec1-dde76ce985fd')

    # Change values by changing the attributes, then calling save().
    >>> q.question_text = "What's up?"
    >>> transaction.commit()

    # Now all() displays all the questions in the database.
    >>> dbsession.query(Question).all()
    [<myapp.models.Question at 0x10e3ef400>]

Wait a minute. ``<myapp.models.Question at 0x10e3ef400>`` is, utterly, an unhelpful representation of this object. Let’s fix that by editing the Question model and adding a `__repr__()` method to both Question and Choice. Python's ``__repr__()`` is the string presentation of the object for shells and debuggers. We also add ``__str()__`` which is later used by admin web interface::

    class Question(Base):

        # ...

        def __repr__(self):
            return "#{}: {}".format(self.id, self.question_text)

        def __str__(self):
            """Python default and admin UI string presentation."""
            return self.question_text


    class Choice(Base):

        # ...

        def __repr__(self):
            """Shell and debugger presentation."""
            return "#{}: {}".format(self.id, self.choice_text)

        def __str__(self):
            """Python default and admin UI string presentation."""
            return self.choice_text


Note these are normal Python methods. Let’s add a custom method, just for demonstration. We update imports with ``datetime`` and ``now`` and add another method to the model body::

    import datetime
    from uuid import uuid4

    from sqlalchemy import Column, String, Integer, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship

    from websauna.system.model.meta import Base
    from websauna.system.model.columns import UTCDateTime

    from websauna.utils.time import now


    class Question(Base):

        #: Relationship mapping between question and choice
        choices = relationship("Choice", back_populates="question")

        # Add model methods after attributes

        def is_recent(self):
            return self.published_at >= now() - datetime.timedelta(days=1)

        # ...

Save the changes. Restart your :term:`notebook` session by shutting it down and starting again.

.. code-block:: pycon

    # Make sure our __repr__() addition worked.
    >>> dbsession.query(Question).all()
    [#1: What's up?]

    # SQLAlchemy provides a rich database lookup API

    # Use get() as a shorthand method to get one object by primary key
    >>> dbsession.query(Question).get(1)
    #1: What's up?

    # Using direct keywords with filter_by()
    >>> dbsession.query(Question).filter_by(id=1).first()
    #1: What's up?

    # Using column objects with filter() and Python comparison operators
    >>> dbsession.query(Question).filter(Question.id==1).first()
    #1: What's up?

    # Text matching query with SQLAlchemy's like()
    >>> dbsession.query(Question).filter(Question.question_text.like('What%')).all()
    [#1: What's up?]

    # Get the question that was published this year.
    >>> dbsession.query(Question).filter(sqlalchemy.extract('year', Question.published_at) == now().year).all()
    [#1: What's up?]

    # Request an ID that doesn't exist by get() returns None
    >>> dbsession.query(Question).get(2)

    # If we want to raise an exception when the row does
    # not exist we can use
    >>> dbsession.query(Question).filter(Question.id==2).one()
    Traceback (most recent call last):
        ...
    NoResultFound: No row was found for one()

    # Make sure our custom method worked.
    >>> q = dbsession.query(Question).get(1)
    >>> q.is_recent()
    True

    # Give the Question a couple of Choices. The create call constructs a new
    # Choice object, does the INSERT statement, adds the choice to the set
    # of available choices and returns the new Choice object. SQLAlchemy creates
    # a set to hold the "other side" of a ForeignKey relation
    # (e.g. a question's choice) which can be accessed via the API.
    >>> q = dbsession.query(Question).get(1)

    # Display any choices from the related object set -- none so far.
    >>> q.choices
    []

    # Create three choices.
    >>> q.choices.append(Choice(choice_text='Not much', votes=0))
    >>> q.choices.append(Choice(choice_text='The sky', votes=0))
    >>> c = Choice(choice_text='Just hacking again', votes=0)
    >>> q.choices.append(c)

    # Choice objects have API access to their related Question objects.
    >>> c.question
    #1: What's up?

    # And vice versa: Question objects get access to Choice objects.
    >>> q.choices
    [#None: Not much, #None: The sky, #None: Just hacking again]

    # Let's flush the database to get ids for our choices
    >>> dbsession.flush()
    >>> q.choices
    [#1: Not much, #2: The sky, #3: Just hacking again]

    >>> len(q.choices)
    3

    # Let's save this everything to database
    >>> transaction.commit()

    # Using SQLAlchemy's join() we can do queries which span across relatinships.
    # Below get all choices for questions made this year.
    >>> dbsession.query(Choice).join(Question).filter(sqlalchemy.extract('year', Question.published_at) == now().year).all()
    [#1: Not much, #2: The sky, #3: Just hacking again]

    # Let's delete one of the choices. Use dbsession.delete() for that.
    >>> c = dbsession.query(Choice).filter_by(choice_text='Just hacking again').first()
    >>> dbsession.delete(c)
    >>> transaction.commit()

More information
================

See :doc:`models documentation <../../narrative/modelling/models>` for more information.
