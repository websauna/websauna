======================
Enter IPython Notebook
======================

Websauna offers integrated :doc:`IPython Notebook shell <../../narrative/misc/notebook>` on the site. It's the most powerful friend for diagnostics, data analysis and poking your database.

Here we show how to enter to the IPython Notebook and create additional user through Python shell.

The notebook shell will be extensively used in the following chapter of this tutorial.

Enter notebook
--------------

You can enter notebook in two ways

* *Shell* link in the top navigation bar opens a global notebook session

* Each item in admin interface has its own *shell* link which oepns a notebook session prepopulated with this item

In this tutorial we are going to use the latter way. Go to admin and click your own user. Then click *Shell* link next to *Set password*.

.. note ::

    Firing up the shell takes some seconds as IPython Notebook is heavyish.

.. image:: images/enter_notebook.png
    :width: 640px

Using shell
-----------

Let's change the name of your user through shell.

Shell exposes the current admin item as ``obj`` variable as shown in the shell instructions.

.. image:: images/notebook.png
    :width: 640px

Type in shell (you can use TAB key for autocomplete variable names and functions)::

    obj.full_name = "The king of Python"
    transaction.commit()

Press ALT + Enter to execute the current contents of the cell in notebook. There is no output for a successful command, because the last line in the cell (``transaction.commit``) returns ``None``.

The latter line is important, because unlike when processing HTTP requests, in shell transactions are not automatically committed. For more information this you can read :doc:`database documentation chapter <../../../narrative/modelling/database>`.

.. image:: images/notebook_changes.png
    :width: 640px

Exit notebook
-------------

You can shut down the notebook by pressing *[ shutdown ]* link in the top. Now navigate back to your user in admin. You see its name has been updated.

.. image:: images/updated_user.png
    :width: 640px

