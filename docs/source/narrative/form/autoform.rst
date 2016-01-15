=========================
Automatic form generation
=========================

Websauna comes with automatic :term:`CRUD` for generation for :term:`SQLAlchemy` models. It can be used standalone from CRUD, too.

Form generator
==============

See :py:meth:`websauna.system.form.fieldmapper.DefaultFieldMapper.map` for interface.

See :py:meth:`websauna.system.crud.views.FormView.create_form` for a usage example.

See classes in :py:mod:`websauna.system.user.adminviews` for examples how to customize automatically included fields.