=================
Automated testing
=================

Introduction
============

Automated testing has various purposes

* It ensures that no new bugs are introduced when software is changed (regression).

* It makes sure that all lines of code are executed at least once without an error (coverage).

* It communicates the indent of the code to other developers lie is how you should use this function (communication). This is especially important in projects with large teams and open source where maintainers do not work in the same physical location every day.

Automated testing is not a substitution for quality assurance, human testers and usability research. It is merely a development process internal tool to ensure that development process flows in a controlled manner and the development team can move forward fast. Regardless of amount of automated testing the software may still be inferior quality wise.

Test types
==========

Before moving forward it's important to understand different test types

* **Unit tests** are laser precise tests which stress out a single function or algorithm. Unit tests often :term:`mock` out parts of the framework and external dependencies for a test run. Websauna itself barely contains any unit tests, because it integrates other components to a high level framework and those components have their own test suites.

* **Functional tests** test one view or views in a separation from others. They either invoke the view using a test request instead of a normal HTTP request object and then parse the response codes and payload. An example of functional test is :py:func:`websauna.tests.test_csrf.test_csrf_exempt`.

* **Integration tests** are the heavy ones. Integration tests ramp up the whole framework for running tests. They usually launch a web browser and have a database for running. Test perform high level actions like "Login to a website" and "press an Add item button" and "fill in the form". :term:`Splinter` is an excellent library for integration testing. An example test is a :py:func:`websauna.tests.test_facebook.test_facebook_first_login` which authenticates a Websauna user against a Facebook and see the user logs in to the site correctly. This test does not mock out anything, but actually checks that facebook.com works with Websauna.

* **Acceptance tests** are high level tests like integration tests. Their political meaning, however, is different. Acceptance tests are usually written with a customer and set the target goals the software must pass for the contract to be fulfilled. Acceptance tests can be written in a very high level description language like :term:`Robot Framework` so that even people without any technical skills can understand the test structure. Websauna does not contain any acceptance tests, as it is not a business project and all stakeholders are developers.

Testing in Websauna
===================

Websauna uses a :term:`pytest` testing framework, with term :term:`Splinter` browser emulation library.

* py.test provides advanced test running capabilities with markers for test exclusion and scope of a test

* Splinter allows easily write functional and integration tests which simulate user browsing behavior on a site

As Websauna integrates a lot of components to a framework, internally Websauna heavily relies on integration testing.

More information
================

Read `testing in Pyramid <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/testing.html>`_.

