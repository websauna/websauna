"""
These tests aim to ensure that websauna's ``simple_route`` can be used in the
same way as pyramid's ``view_config``. Tests are inspired by pyramid's
`viewconfig documentation`_ and aim to check that the provided examples of the
use of ``view_config`` are also applicable to ``simple_route``.

.. _`viewconfig documentation`: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/viewconfig.html#adding-view-configuration-using-the-view-config-decorator

"""
# Pyramid
from pyramid import testing

import pytest
from webtest import TestApp as App


@pytest.fixture(scope='module')
def config():
    with testing.setUp() as config:
        config.scan('websauna.tests.viewconfig.simple_route_tests_views')
        yield config


@pytest.fixture(scope='module')
def testapp(config):
    yield App(config.make_wsgi_app())


def test_registered_routes(config):
    expected_routes = [
        'ClassAsAView',
        'MyViewClass.amethod',
        'MyViewClassAttr.amethod',
        'edit',
        'change',
        'foobar',
        'view_callable',
    ]
    actual_routes = [i.name for i in config.get_routes_mapper().get_routes()]
    assert expected_routes == actual_routes


def test_view_callable(testapp):
    res = testapp.get('/path/to/view')
    assert res.body == b'Hello'


def test_route_items(testapp):
    res = testapp.post('/path/to/view/Joe')
    assert res.body == b'{"message": "Hello Joe"}'


def test_class_as_a_view(testapp):
    res = testapp.get('/class-as-a-view')
    assert res.body == b'class-as-a-view'


def test_muliple_simple_route_decorators(testapp):
    res = testapp.get('/edit')
    assert res.body == b'edited!'
    res = testapp.get('/change')
    assert res.body == b'edited!'


def test_method_of_a_class(testapp):
    res = testapp.get('/amethod')
    assert res.body == b'amethod'


def test_class_method_by_attr(testapp):
    res = testapp.get('/class-attr')
    assert res.body == b'class-attr'


def test_registered_routes_docs(config):
    config.get_routes_mapper()
    request = testing.DummyRequest()
    assert request.route_url('view_callable') == 'http://example.com/path/to/view'
    assert request.route_url('foobar', arg='123') == 'http://example.com/path/to/view/123'
    assert request.route_url('edit') == 'http://example.com/edit'
    assert request.route_url('change') == 'http://example.com/change'
    assert request.route_url('ClassAsAView') == 'http://example.com/class-as-a-view'
    assert request.route_url('MyViewClass.amethod') == 'http://example.com/amethod'
    assert request.route_url('MyViewClassAttr.amethod') == 'http://example.com/class-attr'
