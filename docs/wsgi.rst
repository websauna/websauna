====
WSGI
====

Running uWSGI as development server
-----------------------------------

Example::

    uwsgi --virtualenv=../venv --wsgi-file=wsgitest.py --pythonpath=../venv/bin/python --http-websockets --http=127.0.0.1:8008 --processes=4