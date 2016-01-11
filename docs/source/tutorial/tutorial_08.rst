=============================
Adding data and model methods
=============================

Now we have the model declared, but we do not yet have an user interface to manipulate questions and choices. However, we can do it from the shell.

In this tutorial chapter we show how to pop up :term:`notebook`

Enter the notebook shell
========================

Like earlier, we can enter :term:`notebook`. This time we should see our model in the default variable list:

.. image:: images/question_model.png
    :width: 640px


Playing with the model API
==========================

Once you are in the shell, explore the model :term:`SQLAlchemy` API:

.. note ::

    You can use TAB key for autocompleting variable names. Just type few letters and hit tab and notebook will fill it for you.

::

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

    # Access model field values via Python attributes.
    >>> q.question_text
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

Wait a minute. <myapp.models.Question at 0x10e3ef400> is, utterly, an unhelpful representation of this object. Let’s fix that by editing the Question model and adding a `__repr__()` method to both Question and Choice. Python's ``__repr__()`` is the string presentation of the object for shells and debuggers::

    class Question(Base):

        # ...

        def __repr__(self):
            return "#{}: {}".format(self.id, self.question_text)


    class Choice(Base):

        # ...

        def __repr__(self):
            return "#{}: {}".format(self.id, self.choice_text)

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

    # Make sure our __repr__() addition worked.
    >>> dbsession.query(Question).all()
    [#1: What's up?]

    # SQLAlchemy provides a rich database lookup API

    # Use get() to get one object by primary key
    >>> dbsession.query(Question).get(1)
    #1: What's up?

    # Using direct keywords with filter_by()
    >>> dbsession.query(Question).filter_by(id=1).first()
    #1: What's up?

    # Using column objects with filter() and Python comparison operators
    >>> dbsession.query(Question).filter(Question.id==1).first()
    #1: What's up?

    >>> Question.objects.filter(question_text__startswith='What')
    [<Question: What's up?>]

    # Get the question that was published this year.
    >>> from django.utils import timezone
    >>> current_year = timezone.now().year
    >>> Question.objects.get(pub_date__year=current_year)
    <Question: What's up?>

    # Request an ID that doesn't exist, this will raise an exception.
    >>> Question.objects.get(id=2)
    Traceback (most recent call last):
        ...
    DoesNotExist: Question matching query does not exist.

    # Lookup by a primary key is the most common case, so Django provides a
    # shortcut for primary-key exact lookups.
    # The following is identical to Question.objects.get(id=1).
    >>> Question.objects.get(pk=1)
    <Question: What's up?>

    # Make sure our custom method worked.
    >>> q = Question.objects.get(pk=1)
    >>> q.was_published_recently()
    True

    # Give the Question a couple of Choices. The create call constructs a new
    # Choice object, does the INSERT statement, adds the choice to the set
    # of available choices and returns the new Choice object. Django creates
    # a set to hold the "other side" of a ForeignKey relation
    # (e.g. a question's choice) which can be accessed via the API.
    >>> q = Question.objects.get(pk=1)

    # Display any choices from the related object set -- none so far.
    >>> q.choice_set.all()
    []

    # Create three choices.
    >>> q.choice_set.create(choice_text='Not much', votes=0)
    <Choice: Not much>
    >>> q.choice_set.create(choice_text='The sky', votes=0)
    <Choice: The sky>
    >>> c = q.choice_set.create(choice_text='Just hacking again', votes=0)

    # Choice objects have API access to their related Question objects.
    >>> c.question
    <Question: What's up?>

    # And vice versa: Question objects get access to Choice objects.
    >>> q.choice_set.all()
    [<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]
    >>> q.choice_set.count()
    3

    # The API automatically follows relationships as far as you need.
    # Use double underscores to separate relationships.
    # This works as many levels deep as you want; there's no limit.
    # Find all Choices for any question whose pub_date is in this year
    # (reusing the 'current_year' variable we created above).
    >>> Choice.objects.filter(question__pub_date__year=current_year)
    [<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]

    # Let's delete one of the choices. Use delete() for that.
    >>> c = q.choice_set.filter(choice_text__startswith='Just hacking')
    >>> c.delete()

More information
================

See :doc:`models documentation <../narrative/manipulation/models>` for more information.