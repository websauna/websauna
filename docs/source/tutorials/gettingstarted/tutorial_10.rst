========================
Creating your first view
========================

.. contents:: :local:

A :term:`View` is a Python function or class which serves a certain URL endpoint. A view is a “type” of Web page in your Websauna application, that generally serves a specific function and has a specific template. For example, in a blog application, you might have the following views:

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

In Websauna, web pages and other content are delivered by views. Each view is represented by a simple Python function (or method, in the case of class-based views). Websauna will choose a view by examining the path of the requested URL.

A URL pattern is simply the general form of a URL - for example: `/newsarchive/<year>/<month>/`.

This tutorial provides basic instructions for the use of routing, and you can refer to :ref:`views` for more information.

URL dispatch
------------

In order to get from an URL to a view, Websauna uses what is known as a :term:`router` from :term:`Pyramid` framework. A router maps URL patterns to views. This process is called :term:`URL dispatch`. It is the more common way of building web applications.

Traversal
---------

Websauna also supports an alternative routing method called :term:`traversal`. In traversal, each part of the path maps to a Python object. On a traditional file system, these are folders and files. In Pyramid they are called :term:`resources <resource>`. Resources offer more flexibility and often make the code simpler and elegant for such cases, where hierarchical structure is needed. E.g. all views behind a organization URL are visible for the organization members only. Organization administrators get access to priviledged part of management views. If the users are members of sub-organizations, they can access their specific sub-organizational parts only.

Writing views
-------------

The ``websauna_app`` scaffold has generated a ``views.py`` for you.

Let's add a couple of views there, now.

TODO

Write views that actually do something
--------------------------------------

Each view is responsible for doing one of the following things:

* Returning an :py:class:`pyramid.response.Response` object containing the content for the requested page.

* Returning one of the HTTP error code instances found in :py:mod:`pyramid.httpexceptions`. Don't let the name fool you - you can also just return this.

* Raising an exception - in case of an exception, the :term:`transaction` is rolled back and all changes to the database are reverted.

* Returning an object for ``renderer`` - this is usually a dictionary passed on to template processing. This is the most common case and more about this later.

A view can read records from a database, for example. It can use a template system such as Jinja to render HTML pages. It can generate PDF files, output XML, create ZIP files on the fly, return and accept JSON, anything you want, using whatever Python libraries you want.

Because it’s convenient, let us use SQLAlchemy's database API for now, which we covered earlier in the tutorial. Here’s one stab at a new ``home()`` view, which displays the latest 5 poll questions in the database, separated by commas, according to publication date::

    def home(request: Request):
        """Render the site homepage."""
        latest_question_list = request.dbsession.query(Question).order_by(Question.published_at.desc()).all()[:5]
        output = ', '.join([q.question_text for q in latest_question_list])
        return Response(output)

After editing the code click on the home logo to see how it looks like now.

.. image:: images/question_plain.png
    :width: 640px

There’s a problem here, though: the pages appearance is hard-coded in the view. If you want to change the way the page looks, you’ll have to edit the Python code. So let’s use Websauna’s template system to separate the design from code by creating a template for the view. By default, Websauna offers a template system called :term:`Jinja` (specifically Jinja 2). If you have been writing Django templates or any mustache-like templates with ``{{ variable }}`` declarations you should feel right at home.

Your projects :py:meth:`websauna.system.Initializer.configure_templates` describes how Pyramid will load and render templates. In the generated project scaffold, the folder ``myapp/templates`` was created for them. There exists a template ``myapp/home.html`` already.

.. admonition:: Template namespacing

    Now we *might* be able to get away with putting our templates directly in
    ``myapp/templates`` (rather than creating another ``myapp`` subdirectory),
    but it would actually be a bad idea. Jinja will choose the first template
    it finds whose name matches, and if you had a template with the same name
    in a *different* application, Jinja would be unable to distinguish between
    them. We need to be able to point Jinja to the right one, and the easiest
    way to ensure this is by *namespacing* them. That is, by putting those
    templates inside *another* directory named as the application itself.


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

This code loads the template called  ``myapp/home.html`` and passes it a template context. The context is a dictionary mapping template variable names to Python objects. In this case we pass all local variables from inside view function.

::

    return locals()

Which is a short hand to say::

    return dict(latest_question_list=latest_question_list)

The template itself extends a default base template called ``site/base.html``. That renders :term:`Bootstrap` decoration, namely the header with navigation bar and footer, around your content. You can read more about default templates in :doc:`templates documentation <../../narrative/frontend/templates>`.

Note that we do not refer to the question by its database ``id`` attribute. Instead we use a randomly generated :term:`uuid` attribute and convert it to a :term:`slug` - a string, that looks similar to ``Hh4D7Hh7SWujcvwE0XgEFA``. It is base64 encoded string of 122-bit of randomness. Using UUIDs instead of database attributes in publicly visible content is important for security and business intelligence by reducing the attackable surface of your site for any malicious actors.

The link itself is formed using :py:meth:`pyramid.request.Request.route_url`. It takes a route name (``detail``) and specifies the parameter required for this route. This resolves to the actual URL where the view is configured. This allows you to easily update publicly facing site URLs without need for hardcoded paths in every template.

Load the page by pointing your browser at home, and you should see a
bullet-list containing the "What's up" question from earlier this tutorial.
The link points to the question's detail page. Note: to have this working, you need to add the ``detail`` route and template from below.

.. image:: images/question_home.png
    :width: 640px

Raising a 404 error
===================

Now, let's tackle the question detail view -- the page that displays the question text
for a given poll. Here's the view:

.. code-block:: python

    from pyramid.httpexceptions import HTTPNotFound
    from websauna.utils.slug import slug_to_uuid
    from websauna.system.core.route import simple_route

    @simple_route("/questions/{question_uuid}", route_name="detail", renderer="myapp/detail.html")
    def detail(request):

        # Convert base64 encoded UUID string from request path to Python UUID object
        question_uuid = slug_to_uuid(request.matchdict["question_uuid"])

        question = request.dbsession.query(Question).filter_by(uuid=question_uuid).one_or_none()
        if not question:
            raise HTTPNotFound()
        return locals()

A new concept here: The view raises the :py:class:`pyramid.httpexceptions.HTTPNotFound` exception
if a question with the requested ID doesn't exist.

The route also takes one input parameter - this is the UUID slug in its base64 encoded format, as discussed earlier. :py:func:`websauna.system.core.route.decode_uuid` predicate decodes this automatically for us for Python's :py:class:`uuid.UUID` object.

Use the template system
=======================

Back to the ``detail()`` view for our poll application. Given the context
variable ``question``, here's what the ``myapp/detail.html`` template might look
like:

.. code-block:: html+jinja

    {% extends "site/base.html" %}

    {% block content %}

    <h1>{{ question.question_text }}</h1>
    <ul>
    {% for choice in question.choices %}
        <li>{{ choice.choice_text }}</li>
    {% endfor %}
    </ul>

    {% endblock %}


.. image:: images/question_detail.png
    :width: 640px

We will describe the first, second and last line in a minute. For now, look at the rest.
The template system uses dot-lookup syntax to access variable attributes. In
the example of ``{{ question.question_text }}``, first Jinja does a dictionary lookup
on the object ``question``. Failing that, it tries an attribute lookup -- which
works, in this case. If attribute lookup had failed, it would've tried a
list-index lookup.

In the ``{% for %}`` loop, we iterate over the items of ``question.choices``, which are
the related database records of this question. Cool, isn't it?

