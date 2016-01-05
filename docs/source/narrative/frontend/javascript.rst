==========
JavaScript
==========

Exposing view variables to JavaScript
-------------------------------------

Supposedly one wants to access Python data in JavaScript code. You can do this by returning Javascript objects as dictionaries from the view and then include them as JavaScript globals using `<script>` tag.

It's best to use ``custom_script`` template block before closing ``<body>`` to include all the variables.

First return data as Python dictionaries from your view::

    def my_view(request):
        # ...
        return dict(my_data=dict(a=1, b=2))

Then expose this data to JavaScript by converting it to a JSON object. Please note that due to security concerns we need to pay special attention when embedding data inside ``<script>`` tags::

    {% block custom_script %}
    <script>
        // This global object holds al exposed variables
        window.opt = window.opt || {};
        window.opt.myData = JSON.parse("{{my_data|escape_js}}");
    </script>

You can also expose URLs so that JavaScript can do AJAX calls or ``window.location`` redirects::

    {% block custom_script %}
    <script>
        window.opt = window.opt || {};
        window.opt.pricingURL = "{{ 'price_phone_order'|route_url }}";
    </script>