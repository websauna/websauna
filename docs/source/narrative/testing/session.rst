======================
User sessions in tests
======================

.. contents:: :local:

Accesing session cookie with Splinter
=====================================

Below is an example how you can export a session cookie from Splinter browser and then use this with :py:mod:`requests`. This is especially useful for checking non-HTML responses that :term:`Selenium` is not able to cope with.


