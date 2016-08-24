==============
Writing a form
==============

We're continuing the Web-poll application and will focus on simple form processing and cutting down our code.

.. contents:: :local:

Creating form template
======================

Let's update our poll detail template ``myapp/detail.html`` from the last
chapter, so that the template contains an HTML ``<form>`` element:

.. code-block:: html+jinja

    {% extends "site/base.html" %}

    {% block extra_head %}
    <style>
      .form-vote {
        margin: 20px 0;
      }
    </style>
    {% endblock %}

    {% block content %}
        <h1>{{ question.question_text }}</h1>

        {% if error_message %}
          <div class="alert alert-danger">
            {{ error_message }}
          </div>
        {% endif %}

        <form class="form-vote" action="{{ 'vote'|route_url(question_uuid=question.uuid|uuid_to_slug) }}" method="post">
          <input name="csrf_token" type="hidden" value="{{ request.session.get_csrf_token() }}">


          {% for choice in question.choices %}
            <div class="radio">
              <label for="choice{{ loop.counter }}">
                <input type="radio"
                       name="choice"
                       value="{{ choice.uuid|uuid_to_slug }}">
                {{ choice.choice_text }}
              </label>
            </div>
          {% endfor %}

          <button type="submit" class="btn btn-default">
            Vote
          </button>
        </form>
    {% endblock %}

It looks pretty much this:

.. image:: images/question_form.png
    :width: 640px

A quick rundown:

* The above template displays a radio button for each question choice. The
  ``value`` of each radio button is the associated question choice's ID. The
  ``name`` of each radio button is ``"choice"``. That means, when somebody
  selects one of the radio buttons and submits the form, it'll send the
  POST data ``choice=#`` where # is the base64 encoded :term:`UUID` of the selected choice. This is the
  basic concept of HTML forms.

* We set the form's ``action`` to ``{{ 'vote'|route_url(question_uuid=question.uuid|uuid_to_slug) }}``, and we
  set ``method="post"``. Using ``method="post"`` (as opposed to
  ``method="get"``) is very important, because the act of submitting this
  form will alter data server-side. Whenever you create a form that alters
  data server-side, use ``method="post"``. This tip isn't specific to
  Websauna; it's just good Web development practice.

* ``loop.counter`` indicates how many times the ``for`` tag has gone
  through its loop

* Since we're creating a POST form (which can have the effect of modifying
  data), we need to worry about Cross Site Request Forgeries (:term:`CSRF`).
  Thankfully, you don't have to worry too hard, because Websauna comes with
  a very easy-to-use system for protecting against it. In short, all POST
  forms that are targeted at internal URLs should use the
  ``{{ request.session.get_csrf_token() }}`` to get a session-based token
  which implies a genuine form post by the visitor.

* The form submission result is shown in a :term:`Bootstrap` alert message

* We add some basic :term:`CSS` styling and format form widgets according to :term:`Bootstrap` style guide

Writing form handler
====================

Now, let's create a Websauna view that handles the submitted data and does
something with it. Earlier our implementation of the ``detail()`` function only viewed the results. Let's
create a version which also allows process the votes. Edit the following to ``myapp/views.py``:

.. code-block:: python

    # ...
    from pyramid.httpexceptions import
    from pyramid.session import check_csrf_token
    from websauna.utils.slug import slug_to_uuid
    from websauna.utils.slug import uuid_to_slug
    from websauna.system.core import messages
    # ...

    @simple_route("/questions/{question_uuid}", route_name="detail", renderer="myapp/detail.html")
    def detail(request: Request):

        # Convert base64 encoded UUID string from request path to Python UUID object
        question_uuid = slug_to_uuid(request.matchdict["question_uuid"])

        question = request.dbsession.query(Question).filter_by(uuid=question_uuid).first()
        if not question:
            raise HTTPNotFound()

        if request.method == "POST":

            # Check that CSRF token was good
            check_csrf_token(request)

            question = request.dbsession.query(Question).filter_by(uuid=question_uuid).first()
            if not question:
                raise HTTPNotFound()

            if "choice" in request.POST:
                # Extracts the form choice and turn it to UUID object
                chosen_uuid = slug_to_uuid(request.POST['choice'])
                selected_choice = question.choices.filter_by(uuid=chosen_uuid).first()
                selected_choice.votes += 1
                messages.add(request, msg="Thank you for your vote", kind="success")
                return HTTPFound(request.route_url("results", question_uuid=uuid_to_slug(question.uuid)))
            else:
                error_message = "You did not select any choice."

        return locals()

This code includes a few things we haven't covered yet in this tutorial:

* :attr:`request.POST <pyramid.request.Request.POST>` is a dictionary-like
  object that lets you access submitted data by key name. In this case,
  ``request.POST['choice']`` returns the base64 encoded UUID of the selected choice, as a
  string.

  Note that Pyramid also provides :attr:`request.GET <pyramid.request.Request.GET>` for accessing GET data in the same way --
  but we're explicitly using POST in our code, to ensure that data is only
  altered via a POST call.

* We check if the choice is present in the form and skip to ``error_message`` if a visitor submits an empty form

* We increment the vote count of a choice on a successful submit. We add a success message to the :doc:`flash message stack <../../narrative/misc/messages>` which is a displayed on the results page after redirect.

.. note ::

    **Why there is no save()?**

    :term:`SQLAlchemy` has a :term:`state management` mechanism. It tracks what objects you have modified or added via ``dbsession.add()``. On a succesfull commit, all of these changes are written to a database and you do not need to explicitly list what changes need to be saved.

.. note ::

    **What happens if requests modify data simultaneously?**

    Websauna uses an :term:`optimistic concurrency control` strategy with atomic requests.
    Optimistic concurrency control protects your application against a :term:`race condition`.

    The default database transaction :term:`isolation level` is serializable: database prevents race conditions to happen. If a database detects a race condition an application level Python exception is raised. Then the application tries to resolve this conflict. Websauna default resolution mechanism is through :term:`transaction retry`.

.. note ::

    **A form framework reduces your workload**

    In real life you rarely need to write forms by hand in Websauna. Here we do it for practice. Instead you want to use a :term:`Deform` form framework. Deform comes with dozens widgets and validators, as writing all HTML and validation code for complex forms would be a massive effort. Furthermore forms :doc:`can be automatically generated from the SQLAlchemy models <../../narrative/form/autoform>` like admin interface does.

Showing results
===============

Let's start by creating a ``myapp/results.html`` template:

.. code-block:: html+jinja

    {% extends "site/base.html" %}

    {% block content %}
      <h1>{{ question.question_text }}</h1>

      <ul>
        {% for choice in choices %}
            <ol>{{ choice.choice_text }} -- {{ choice.votes }} votes</ol>
        {% endfor %}
      </ul>

      <a href="{{ 'detail'|route_url(question_uuid=question.uuid|uuid_to_slug) }}">Vote again?</a>
    {% endblock %}


Then let's modify our ``results`` view function::

    # ...
    from myapp.models import Choice
    # ...

    @simple_route("/questions/{question_uuid}/results", route_name="results", renderer="myapp/results.html")
    def results(request: Request):

        # Convert base64 encoded UUID string from request path to Python UUID object
        question_uuid = slug_to_uuid(request.matchdict["question_uuid"])

        question = request.dbsession.query(Question).filter_by(uuid=question_uuid).first()
        if not question:
            raise HTTPNotFound()
        choices = question.choices.order_by(Choice.votes.desc())
        return locals()

Now we can the answer we all have been waiting for:

.. image:: images/question_results.png
    :width: 640px
