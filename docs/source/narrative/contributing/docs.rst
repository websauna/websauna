=============
Documentation
=============

Building documentation
----------------------

Websauna documentation is managed with Sphinx.

Use Sphinx 2.x:

.. code-block:: console

    pip install "Sphinx<3"

To build the documentation, inside the websauna repository, execute:

.. code-block:: console

    cd docs
    make all

Copy docs over to the Netlify site:

.. code-block:: console

    cp -r build/html/ ../../site/output/docs/

This will generate the complete documentation, including:

    * APIdoc
    * Reference
    * Tutorials
    * Ansible playbook

Both in html and epub formats.
