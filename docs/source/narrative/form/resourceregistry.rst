===================================
Resource registry and widget assets
===================================

Deform supports resource registry (:py:class:`websauna.system.form.resourceregistry.ResourceRegistry`) which widgets can use to signal they want a particular CSS and JS file to be present in the page rendering

* Form is constructed with ``resource_registry`` argument

* When the form is finalized, before the page rendering starts call :py:meth:`websauna.system.form.resourceregistry.ResourceRegistry.pull_resources`

* This will go through the form widget stack and extract CSS and JS files from widgets. The required files are passed to :py:class:`websauna.system.core.render.OnDemandResourceRenderer`

* JS is included in ``site/javascript.html`` template and CSS is included in site ``site/css.html`` template.

* By default ``<script>`` tags comes before closing of ``</body>``. If any Deform widgets require JS all ``<script>`` goes to ``<head>``. This is due to current Deform template limitations.

Deform comes with some default Bootstrap-compatible JS and CSS files, see :py:attr:`deform.widget.default_resources`. Resource registry can also manage bundling of the resources, so that instead of pulling the actual JS file it pulls a bundle where this JS file is present.