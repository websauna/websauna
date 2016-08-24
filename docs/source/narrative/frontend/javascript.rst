==========
JavaScript
==========

.. contents:: :local:

Introduction
============

Websauna supports integration with various JavaScript libraries.

See also :ref:`cache busting <cachebust>` how Websauna guarantees client JavaScript files are always up-to-date.

Adding JavaScript code to a specific page
=========================================

Below is an example how to integrate a JavaScript library and its integration code to one specific page. In this example we add an enhanced file upload experience using a `DropzoneJS JavaScript library <http://localhost:6543/upload-invoice>`_.

First you must add ``dropzone`` folder to :ref:`static assets <static>` of your application.

.. image:: ../images/upload-invoice.png
    :width: 640px

Referring JavaScript assets on a page
-------------------------------------

A custom JavaScript files are added to a `extra_body_end` block, so that they are loaded after all site default JavaScript.

A library CSS files are placed in ``extra_head`` block, so that library styles are available during the initial page rendering and there is no flicker. See :ref:`base.html template <template-site/base.html>` for more information about blocks.

Example ``upload_invoice.html``:

.. code-block:: html+jinja

    {# Use the defaut page framing #}
    {% extends "site/base.html" %}

    {# Include DropzoneJS CSS on the page in <head> #}
    {% block extra_head %}
      <link rel="stylesheet" href="{{ 'myapp:static/dropzone/dropzone.css'|static_url }}">
    {% endblock %}

    {# Content block contains the body HTML #}
    {% block content %}
        <h1>Upload invoice</h1>
        <form id="form-upload-invoice" class="dropzone" method="POST" action="">
        </form>

    {% endblock content %}

    {# extra_body_end has everything specific to this page before closing </body> #}
    {% block extra_body_end %}
      <script>
        {# Here are variables we pass to our integration JavaScript  #}
        window.opt = {
          uploadTarget: "{{ 'upload_invoice'|route_url }}",
          csrfToken: "{{ request.session.get_csrf_token() }}"
        };
      </script>

      {# Include DropzoneJS JS on the page  #}
      <script src="{{ 'myapp:static/dropzone/dropzone.js'|static_url }}"></script>

      {# Include our integration JS on the page  #}
      <script src="{{ 'myapp:static/dropzone-integration.js'|static_url }}"></script>
    {% endblock %}

Example ``dropzone-integration.js``:

.. code-block:: javascript

    /* global Dropzone, Query */

    // Disabling autoDiscover, otherwise Dropzone will try to attach twice.
    Dropzone.autoDiscover = false;

    (function($) {
      "use strict";

      // Executed when DOM parsing is done
      $(document).ready(function() {

        // Create our file dropzone through jQuery
        // http://www.dropzonejs.com/#create-dropzones-programmatically
        var dz = $("#form-upload-invoice").dropzone({
          url: window.opt.uploadTarget,
          dictDefaultMessage: ">>> Drop your invoice XML file here <<<",
          sending: function(file, xhr, formData) {
            // Include Websauna CSRF token for the form submission
            formData.append("csrf_token", window.opt.csrfToken);
          }
        });

      });

    })(jQuery);

Then you can process the upload in your ``views.py`` - this AJAX upload does not differ from a normal HTTP POST upload:

.. code-block:: python

    @simple_route("/upload-invoice",
                  route_name="upload_invoice",
                  renderer='myapp/upload_invoice.html')
    def upload_invoice(request: Request):
        """Render an invoice upload form and process uploads."""

        if request.method == "POST":
            # This is a cgi.FieldStorage instance
            file = request.POST["file"]
            # Process upload
            # ...

        return locals()

Exposing view variables to JavaScript
=====================================

Supposedly one wants to access Python data in JavaScript code. You can do this by returning Javascript objects as dictionaries from the view and then include them as JavaScript globals using `<script>` tag.

It's best to use ``extra_body_end`` template block before closing ``<body>`` to include all the variables.

First return data as Python dictionaries from your view::

    def my_view(request):
        # ...
        return dict(my_data=dict(a=1, b=2))

Then expose this data to JavaScript by converting it to a JSON object. Please note that due to security concerns we need to pay special attention when embedding data inside ``<script>`` tags::

    {% block extra_body_end %}
    <script>
        // This global object holds all exposed variables
        window.opt = window.opt || {};
        window.opt.myData = JSON.parse("{{my_data|escape_js}}");
    </script>

You can also expose URLs so that JavaScript can do AJAX calls or ``window.location`` redirects::

    {% block extra_body_end %}
    <script>
        window.opt = window.opt || {};
        window.opt.pricingURL = "{{ 'price_phone_order'|route_url }}";
    </script>
