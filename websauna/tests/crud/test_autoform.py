"""Test form autogeneration and CRUD."""
# Standard Library
import time

# Pyramid
import transaction

import pytest
from splinter.driver import DriverAPI

# Websauna
import websauna
from websauna.tests.test_utils import create_logged_in_user
from websauna.tests.webserver import customized_web_server
from websauna.utils.slug import slug_to_uuid
from websauna.utils.slug import uuid_to_slug


@pytest.fixture(scope="module")
def tutorial_app(request, paster_config):
    """Custom WSGI app with travesal points for sitemap enabled."""

    class Initializer(websauna.system.DemoInitializer):

        def run(self):
            super(Initializer, self).run()
            from websauna.tests.crud import tutorial
            self.config.scan(tutorial)

    global_config, app_settings = paster_config
    init = Initializer(global_config, app_settings)
    init.run()
    app = init.make_wsgi_app()
    app.init = init
    return app


@pytest.fixture(scope="module")
def web_server(request, tutorial_app):
    """Run a web server with tutorial installed."""
    web_server = customized_web_server(request, tutorial_app)
    return web_server()


@pytest.fixture(scope="module")
def registry(request, tutorial_app):
    """Run a web server with tutorial installed."""
    return tutorial_app.init.config.registry


@pytest.mark.skip("Mark skipped for now before issues resolved on TravisCI - something to do with delays and browsers")
def test_add_question(browser: DriverAPI, registry, web_server, dbsession):
    """Adding questions should be succesful."""

    b = browser

    if b.driver.capabilities["browserName"] != "firefox":
        # Fails at click and JavaScript modals for Chrome
        pytest.skip("This test works only under Firefox WebDriver")

    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit(web_server)
    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-add-question").click()
    b.fill("question_text", "What is love")
    b.find_by_css("#deformField2-date").click()

    # Pick any date
    b.find_by_css(".picker__day--infocus")[0].click()

    time.sleep(0.8)  # Give some time for the browser, next click fails on CI

    b.find_by_css("#deformField2-time").click()
    b.find_by_css(".picker__list-item")[0].click()

    time.sleep(0.5)  # Give some time for the browser, next click fails on CI

    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")


def test_add_choice_no_question(browser: DriverAPI, registry, web_server, dbsession):
    """Add one choice, no questions available."""

    b = browser

    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit(web_server)
    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-add-choice").click()
    b.fill("choice_text", "Baby don't hurt me")
    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")


def test_add_choice_question(browser: DriverAPI, registry, web_server, dbsession):

    from .tutorial import Question
    from .tutorial import Choice

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()
        question_uuid = uuid_to_slug(q.uuid)

    b = browser

    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit(web_server)
    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-add-choice").click()
    b.fill("choice_text", "Baby don't hurt me")
    b.select("question", question_uuid)
    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")

    with transaction.manager:
        assert dbsession.query(Choice).first().question is not None


def test_add_choice_choose_no_question(browser: DriverAPI, registry, web_server, dbsession):

    from .tutorial import Question
    from .tutorial import Choice

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()

    b = browser
    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit(web_server)
    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-add-choice").click()
    b.fill("choice_text", "Baby don't hurt me")
    b.find_by_name("add").click()

    assert b.is_element_present_by_css("#msg-item-added")

    with transaction.manager:
        assert dbsession.query(Choice).first().question is None


def test_edit_choice_question(browser: DriverAPI, registry, web_server, dbsession):
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
    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/choice/{}/edit".format(web_server, c_slug))
    b.select("question", q2_slug)
    b.find_by_name("save").click()

    assert b.is_element_present_by_css("#msg-changes-saved")

    with transaction.manager:
        c = dbsession.query(Choice).get(1)
        assert c.question.uuid == slug_to_uuid(q2_slug)


def test_edit_choice_remove_question(browser: DriverAPI, registry, web_server, dbsession):
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
    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/choice/{}/edit".format(web_server, c_slug))
    b.select("question", "")
    b.find_by_name("save").click()

    assert b.is_element_present_by_css("#msg-changes-saved")

    with transaction.manager:
        c = dbsession.query(Choice).get(1)
        assert c.question is None


def test_question_shows_choices(browser: DriverAPI, registry, web_server, dbsession):
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
    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/question/{}/show".format(web_server, q_slug))
    assert b.is_text_present("Baby don't hurt me")


def test_question_listing(browser: DriverAPI, registry, web_server, dbsession):
    """Question listing shows question text."""

    from .tutorial import Question

    with transaction.manager:
        q = Question(question_text="What is love")
        dbsession.add(q)
        dbsession.flush()

    b = browser
    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/question/listing".format(web_server))
    assert b.is_text_present("What is love")


def test_question_delete(browser: DriverAPI, registry, web_server, dbsession):
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
    create_logged_in_user(dbsession, registry, web_server, browser, admin=True)

    b.visit("{}/admin/models/question/{}".format(web_server, q_slug))
    b.find_by_css("#btn-crud-delete").click()
    b.find_by_css("#btn-delete-yes").click()

    with transaction.manager:
        assert dbsession.query(Question).count() == 0
        assert dbsession.query(Choice).count() == 0
