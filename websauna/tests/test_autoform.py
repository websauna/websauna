"""Test form autogeneration and CRUD."""
import time

import os
import pytest
from splinter.driver import DriverAPI
import transaction

from websauna.system.devop.cmdline import init_websauna
from websauna.tests.utils import create_logged_in_user
from websauna.tests.webserver import customized_web_server
from websauna.utils.slug import uuid_to_slug, slug_to_uuid

HERE = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def tutorial_req(request):
    """Construct a WSGI app with tutorial models and admins loaded."""
    ini_file = os.path.join(HERE, "tutorial-test.ini")
    request = init_websauna(ini_file)
    return request


@pytest.fixture(scope="module")
def web_server(request, tutorial_req):
    """Run a web server
    with tutorial installed."""
    web_server = customized_web_server(request, tutorial_req.app)
    return web_server()


def test_add_question(browser: DriverAPI, tutorial_req, web_server, dbsession):
    """Adding questions should be succesful."""

    b = browser

    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit(web_server)
    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-add-question").click()
    b.fill("question_text", "What is love")
    b.find_by_css("#deformField2-date").click()

    # Pick any date
    b.find_by_css(".picker__day--infocus")[0].click()

    time.sleep(0.5)  # Give some time for the browser, next click fails on CI

    b.find_by_css("#deformField2-time").click()
    b.find_by_css(".picker__list-item")[0].click()

    time.sleep(0.5)  # Give some time for the browser, next click fails on CI

    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")


def test_add_choice_no_question(browser: DriverAPI, tutorial_req, web_server, dbsession):
    """Add one choice, no questions available."""

    b = browser

    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit(web_server)
    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-add-choice").click()
    b.fill("choice_text", "Baby don't hurt me")
    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")


def test_add_choice_question(browser: DriverAPI, tutorial_req, web_server, dbsession):

    from .tutorial import Question
    from .tutorial import Choice

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()
        question_uuid = uuid_to_slug(q.uuid)

    b = browser

    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit(web_server)
    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-add-choice").click()
    b.fill("choice_text", "Baby don't hurt me")
    b.select("question", question_uuid)
    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")

    with transaction.manager:
        assert dbsession.query(Choice).first().question is not None


def test_add_choice_choose_no_question(browser: DriverAPI, tutorial_req, web_server, dbsession):

    from .tutorial import Question
    from .tutorial import Choice

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()

    b = browser
    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit(web_server)
    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-add-choice").click()
    b.fill("choice_text", "Baby don't hurt me")
    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")

    with transaction.manager:
        assert dbsession.query(Choice).first().question is None


def test_edit_choice_question(browser: DriverAPI, tutorial_req, web_server, dbsession):
    """Change choice's assigned question in edit."""

    from .tutorial import Question
    from .tutorial import Choice

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()

        q2 = Question(question_text="Who shot JFK")
        dbsession.add(q2)
        dbsession.flush()
        q2_slug = uuid_to_slug(q2.uuid)

        c = Choice(choice_text="Foobar", question=q)
        dbsession.add(c)
        dbsession.flush()
        c_slug = uuid_to_slug(c.uuid)

    b = browser
    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/choice/{}/edit".format(web_server, c_slug))
    b.select("question", q2_slug)
    b.find_by_name("save").click()

    assert b.is_element_present_by_css("#msg-changes-saved")

    with transaction.manager:
        c = dbsession.query(Choice).get(1)
        assert c.question.uuid == slug_to_uuid(q2_slug)


def test_edit_choice_remove_question(browser: DriverAPI, tutorial_req, web_server, dbsession):
    """Editing choice allows us to reset question value back to null."""

    from .tutorial import Question
    from .tutorial import Choice

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()

        c = Choice(choice_text="Foobar", question=q)
        dbsession.add(c)
        dbsession.flush()
        c_slug = uuid_to_slug(c.uuid)

    b = browser
    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/choice/{}/edit".format(web_server, c_slug))
    b.select("question", "")
    b.find_by_name("save").click()

    assert b.is_element_present_by_css("#msg-changes-saved")

    with transaction.manager:
        c = dbsession.query(Choice).get(1)
        assert c.question == None


def test_question_shows_choices(browser: DriverAPI, tutorial_req, web_server, dbsession):
    """If question has active choices they are shown on Show screen, albeit not editable."""

    from .tutorial import Question
    from .tutorial import Choice

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()
        q_slug = uuid_to_slug(q.uuid)

        c = Choice(choice_text="Baby don't hurt me", question=q)
        dbsession.add(c)
        dbsession.flush()

    b = browser
    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/question/{}/show".format(web_server, q_slug))
    assert b.is_text_present("Baby don't hurt me")


def test_question_listing(browser: DriverAPI, tutorial_req, web_server, dbsession):
    """Question listing shows question text."""

    from .tutorial import Question

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()

    b = browser
    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/question/listing".format(web_server))
    assert b.is_text_present("What is love")


def test_question_delete(browser: DriverAPI, tutorial_req, web_server, dbsession):
    """Delete question and make sure it deletes related choices.."""

    from .tutorial import Question
    from .tutorial import Choice

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()

        c = Choice(choice_text="Baby don't hurt me", question=q)
        dbsession.add(c)
        dbsession.flush()
        q_slug = uuid_to_slug(q.uuid)

    b = browser
    create_logged_in_user(dbsession, tutorial_req.registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/question/{}".format(web_server, q_slug))
    b.find_by_css("#btn-crud-delete").click()
    b.find_by_css("#btn-delete-yes").click()

    with transaction.manager:
        assert dbsession.query(Question).count() == 0
        assert dbsession.query(Choice).count() == 0

