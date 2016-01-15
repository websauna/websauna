========================
Creating your first view
========================

.. contents:: :local:

:term:`View` is a Python function or class which serves certain URL endpoint. A view is a “type” of Web page in your Websauna application that generally serves a specific function and has a specific template. For example, in a blog application, you might have the following views:

* Blog homepage – displays the latest few entries.

* Entry “detail” page – permalink page for a single entry.

* Year-based archive page – displays all months with entries in the given year.

* Month-based archive page – displays all days with entries in the given month.

* Day-based archive page – displays all entries in the given day.

* Comment action – handles posting comments to a given entry.

In our poll application, we’ll have the following four views:

* Question “index” page – displays the latest few questions.

* Question “detail” page – displays a question text, with no results but with a form to vote.

* Question “results” page – displays results for a particular question.

* Vote action – handles voting for a particular choice in a particular question.

In Websauna, web pages and other content are delivered by views. Each view is represented by a simple Python function (or method, in the case of class-based views). Websauna will choose a view by examining the URL that’s requested (to be precise, the part of the URL after the domain name).

A URL pattern is simply the general form of a URL - for example: `/newsarchive/<year>/<month>/`.

This tutorial provides basic instruction in the use of routing, and you can refer to :doc:`view documentation <../../narrative/frontend/views>` for more information.

URL dispatch
------------

To get from a URL to a view, Websauna uses what are known as :term:`router` from :term:`Pyramid` framework. A router maps URL patterns to views. This process is called :term:`URL dispatch`. It is the more well known way of building web applications.

Traversal
---------

Websauna supports also alternative routing method, called :term:`traversal`. In traversal each path part of the URL maps to a Python object. On a traditional file systems these are folders and files. In Pyramid they are called :term:`resources <resource>`. Resources offer more flexibility and often make the code more simple and elegant for the cases where hierarchial permissions are needed. E.g. all views behind a organization URL are visible for the organization members only. Organization administrators get access to priviledged part of management views. If the users are members of suborganzations they can access their specific suborganizations only.

Writing views
-------------

The ``websauna_app`` scaffold has generated ``views.py`` for you.

Let's now add couple of more views there.

TODO

Write views that actually do something
--------------------------------------

Each view is responsible for doing one of two things:

* Returning an :py:class:`pyramid.response.Response` object containing the content for the requested page.

* Returning one of HTTP error codes as instance of ones found in :py:mod:`pyramid.httpexcetions`. Don't let the name fool - oyu can also return this instead of raising these.

* Raising an exception - in the case of exception the :term:`transaction` is rolled back and nothing is written to the database

* Returning an object for ``renderer`` - this is usually a dictionary passed to templates. This is the most common case and more about this later.

Your view can read records from a database, or not. It can use a template system such as Websauna’s. It can generate a PDF file, output XML, create a ZIP file on the fly, anything you want, using whatever Python libraries you want.

Because it’s convenient, let’s use SQLAlchemy’s database API, which we covered in earlier in the tutorial. Here’s one stab at a new ``home()`` view, which displays the latest 5 poll questions in the system, separated by commas, according to publication date::

    def home(request: Request):
        """Render the site homepage."""
        latest_question_list = request.dbsession.query(Question).order_by(Question.published_at.desc()).all()[:5]
        output = ', '.join([q.question_text for q in latest_question_list])
        return Response(output)

After editing the code click yourself to your website home by clicking logo to see how this look likes.

.. image:: images/question_plain.png
    :width: 640px

There’s a problem here, though: the page’s design is hard-coded in the view. If you want to change the way the page looks, you’ll have to edit this Python code. So let’s use Websauna’s template system to separate the design from Python by creating a template that the view can use. By default, Websauna offers a template system called :term:`Jinja` (specifically Jinja 2). If you have been writing Django templates or any mustache-like templates with ``{{ variable }}`` declarations you should feel home.

Your project’s :py:meth:`websauna.system.Initializer.configure_templates` describes how Pyramid will load and render templates. In the generated project scaffold, it adds ``myapp/templates`` folder there. There already exists a template called ``myapp/home.html``.

.. admonition:: Template namespacing

    Now we *might* be able to get away with putting our templates directly in
    ``myapp/templates`` (rather than creating another ``myapp`` subdirectory),
    but it would actually be a bad idea. Jinja will choose the first template
    it finds whose name matches, and if you had a template with the same name
    in a *different* application, Jinja would be unable to distinguish between
    them. We need to be able to point Jina at the right one, and the easiest
    way to ensure this is by *namespacing* them. That is, by putting those
    templates inside *another* directory named for the application itself.


Put the following code in ``templates/myapp/home.html``

.. code-block:: html+jinja

    {% extends "site/base.html" %}

    {% block content %}
        {% if latest_question_list %}
            <ul>
            {% for question in latest_question_list %}
                <li>
                  <a href="{{ 'detail'|route_url(question_uuid=question.uuid|uuid_to_slug) }}">
                    {{ question.question_text }}
                  </a>
                </li>
            {% endfor %}
            </ul>
        {% else %}
            <p>No polls are available.</p>
        {% endif %}
    {% endblock %}


Now let’s update our home view in ``myapp/views.py`` to use the template::

    # Configure view named home at path / using a template myapp/home.html
    @simple_route("/", route_name="home", renderer="myapp/home.html")
    def home(request: Request):
        """Render the site homepage."""
        latest_question_list = request.dbsession.query(Question).order_by(Question.published_at.desc()).all()[:5]
        return locals()

That code loads the template called  ``myapp/home.html`` and passes it a template context. The context is a dictionary mapping template variable names to Python objects. In this case we pass all local variables from inside view function.

::

    return locals()

Is a short hand to say::

    return dict(latest_question_list=latest_question_list)

The template itself extends a default base template called ``site/base.html``. This renders :term:`Bootstrap` decoration, namely header with navigation bar and footer, around your content. You can read more about default templates in :doc:`templates documentation <../../narrative/frontend/templates>`.

We do not refer the question by its running counter ``id`` attribute. Instead we take a randomly generated :term:`uuid` attribute and convert it to a :term:`slug` - a string which looks like ``Hh4D7Hh7SWujcvwE0XgEFA``. It is base64 encoded string of 122-bit of randomness. Using UUIDs instead of running counters in publicly visible content is important from the security and business intelligence - this way your malicious actors and competitors have harded to extract meaningful intel out of your site.

The link itself is formed using :py:meth:`pyramid.request.Request.route_url`. It takes a route name (``detail``) and gives parameters required for this route. This resolves to the actual URL where the view is configured. This allows you to easily update publicly facing site URLs without need to fix hardcoded paths in every template.

Load the page by pointing your browser at home, and you should see a
bulleted-list containing the "What's up" question from earlier this tutorial.
The link points to the question's detail page.

.. image:: images/question_home.png
    :width: 640px

Raising a 404 error
===================

Now, let's tackle the question detail view -- the page that displays the question text
for a given poll. Here's the view:

::

    from pyramid.httpexceptions import HTTPNotFound

    @simple_route("/questions/{question_uuid}", route_name="detail", renderer="myapp/detail.html", custom_predicates=(decode_uuid,))
    def detail(request, question_uuid):
        question = request.dbsession.query(Question).filter_by(uuid=question_uuid).first()
        if not question:
            raise HTTPNotFound()
        return locals()

The new concept here: The view raises the :py:class:`pyramid.httpexceptions.HTTPNotFound` exception
if a question with the requested ID doesn't exist.

The route also takes one input parameter - this is the UUID slug in its base64 encoded format, as discussed earlier. :py:func:`websauna.system.core.route.decode_uuid` predicate decodes this automatically for us for Python's :py:class:`uuid.UUID` object.

We'll discuss what you could put in that ``myapp/detail.html`` template a bit
later, but if you'd like to quickly get the above example working, a file
containing just:

.. code-block:: html+jinja

    {{ question }}

will get you started for now.

Use the template system
=======================

Back to the ``detail()`` view for our poll application. Given the context
variable ``question``, here's what the ``myapp/detail.html`` template might look
like:

.. code-block:: html+jinja



    <h1>{{ question.question_text }}</h1>
    <ul>
    {% for choice in question.choice_set.all %}
        <li>{{ choice.choice_text }}</li>
    {% endfor %}
    </ul>

.. image:: images/question_detail.png
    :width: 640px

The template system uses dot-lookup syntax to access variable attributes. In
the example of ``{{ question.question_text }}``, first Jinja does a dictionary lookup
on the object ``question``. Failing that, it tries an attribute lookup -- which
works, in this case. If attribute lookup had failed, it would've tried a
list-index lookup.

Method-calling happens in the ``{% for %}`` loop:
``question.choices`` is interpreted as the Python code
``question.choices``, which returns an iterable of ``Choice`` objects and is
suitable for use in the ``{% for %}`` tag.

