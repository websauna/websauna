======
Themes
======

Websauna default site comes with templates and form widgets for :term:`Bootstrap` 3.x series. Bootstrap is the most popular frontend framework in the world, offering plenty of premium theme packages you can install for your site.

.. contents:: :local:

Getting themes
==============

Free and premium Bootstrap themes can be found e.g. at

* http://bootswatch.com/

* https://wrapbootstrap.com/themes

* http://startbootstrap.com/

* http://bootstrapbay.com/

Installing a Bootstrap theme
============================

Downloading a theme
-------------------

In this example we install a premium theme on your Websauna site based on ``cookiecutter-websauna-app`` :term:`cookiecutter` template.

Bootstrap theme is distributed as a zip file. We download the zip file, extract it and examine its contents::

    assets
    assets/css
    assets/css/main.css
    assets/fonts
    assets/fonts/fontawesome-webfont.eot
    ...
    assets/img
    assets/img/1.png
    assets/img/2.png
    assets/img/3.png
    assets/img/iphone.png
    assets/img/mouse.png
    assets/js
    assets/js/bootstrap-3.1.1.min.js
    assets/js/jquery-1.11.1.min.js
    assets/js/jquery.isotope.min.js
    assets/js/jquery.singlePageNav.min.js
    assets/js/main.js
    assets/less
    assets/less/bootstrap-3.1.1
    assets/less/bootstrap-3.1.1/alerts.less
    ...
    assets/less/bootstrap-3.1.1/wells.less
    assets/less/font-awesome-4.1.0
    assets/less/font-awesome-4.1.0/bordered-pulled.less
    ...
    assets/less/font-awesome-4.1.0/variables.less
    assets/less/main.less
    assets/less/style.less
    assets/less/theme.less
    assets/less/variables.less
    contact.php
    image.php
    images
    images/hero.png
    index.html

The Bootstrap theme is distributed as :term:`Less` source code files and precompiled :term:`CSS` files. It comes with a sample `index.html` example. There are also files for :term:`Font Awesome` icons.

Setting up files
----------------

To simplify the process we first copy the whole ``assets`` folder to ``company/application/static``.

Ignored theme parts
-------------------

Theme contains Font Awesome files and Bootstrap source files. We ignore them and instead of Websauna supplied defaults.

* Websauna has set up Font Awesome to load from their :term:`CDN`

* Websauna comes with up-to-date Bootstrap and CSS files

Setting up CSS
--------------

Edit ``templates/site/css.html`` as provided by :term:`cookiecutter` template:

.. code-block:: html+jinja

    {# Specify CSS section for in the site <head> #}

    {# Include Bootstrap CSS from Websauna core package - http://getbootstrap.com/ #}
    <link rel="stylesheet" href="{{ 'websauna.system:static/bootstrap.min.css'|static_url }}">

    {# Include Font-Awesome icons from CDN - http://fontawesome.io/ #}
    <link href="//netdna.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css" rel="stylesheet">

    {# Include some default Websauna styles, like log out link styles fixes #}
    <link rel="stylesheet" href="websauna.system:static/theme.css">

    <!--

        ... Adding in here ...

    -->
    {# Include CSS from premium theme - see file location from your theme package #}

    <link rel="stylesheet" href="{{ 'company.application:static/assets/css/main.css'|static_url }}">

    {# We leave here a local theme.css file where we can overlay CSS fixes if needed #}
    <link rel="stylesheet" href="{{ 'company.application:static/theme.css'|static_url }}">

    {# Include CSS for widgets #}
    {% if request.on_demand_resource_renderer %}
      {% for css_url in request.on_demand_resource_renderer.get_resources("css") %}
        <link rel="stylesheet" href="{{ css_url }}"></link>
      {% endfor %}
    {% endif %}


Now let's start the site with :ref:`ws-pserve` and we should see the changes (fonts, colors):

.. image :: ../images/theming.png
    :width: 640px

Setting up JavaScript
---------------------

This theme comes with its enhanched JavaScript experience (single page navigation). For now we just ignore this as this JavaScript is relevant only for the example ``index.html`` of the theme.

Making adjustments to theme colors
----------------------------------

Please refer to :term:`Less` and :term:`Bootstrap` tutorials and how to rebuild CSS files from Less source code files using command line tools.