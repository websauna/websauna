import transaction

from pyramid_web20.tests.utils import create_logged_in_user
from pyramid_web20.tests.utils import get_user
from pyramid_web20.models import DBSession


GROUP_NAME = "Sample Group"


def test_add_group(light_web_server, browser, dbsession):
    """Create a new group through admin interface."""

    b = browser
    create_logged_in_user(light_web_server, browser, admin=True)

    b.find_by_css("#nav-admin").click()

    b.find_by_css("#btn-panel-add-group").click()
    b.fill("name", GROUP_NAME)
    b.fill("description", "Foobar")
    b.find_by_name("add").click()

    assert b.is_text_present("Item added")

    # Check we appear in the list
    b.visit("{}/admin/group/listing".format(light_web_server))

    # The description appears in the listing
    assert b.is_text_present("Foobar")


def test_put_user_to_group(light_web_server, browser, dbsession):
    """Check that we can assign users to groups in admin interface."""

    b = browser

    from pyramid_web20.system.user.models import Group

    create_logged_in_user(light_web_server, browser, admin=True)

    # Create a group where we
    with transaction.manager:
        g = Group(name=GROUP_NAME)
        DBSession.add(g)

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-list-user").click()
    b.find_by_css(".crud-row-1 .btn-crud-listing-edit").click()

    # Check the group checkbox. We could put some more specific classes for controls here.
    b.find_by_css("input[type='checkbox'][value='2']").click()
    b.find_by_name("save").click()

    assert b.is_text_present("Changes saved")

    # Now we are on Show page of the user, having the new group name visible
    assert b.is_text_present(GROUP_NAME)



def test_user_group_choices_preserved_on_validation_error(light_web_server, browser, dbsession):
    """When user edit form validation fails, we should preserve the existing group choices.

    This stresses out hacky implementation of pyramid_web20.system.form.colander and deserialization.
    """

    b = browser

    from pyramid_web20.system.user.models import Group

    create_logged_in_user(light_web_server, browser, admin=True)

    # Create a group where we
    with transaction.manager:
        g = Group(name=GROUP_NAME)
        DBSession.add(g)
        u = get_user()
        u.groups.append(g)

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-list-user").click()
    b.find_by_css(".crud-row-1 .btn-crud-listing-edit").click()

    # We are in group 2 initially, assert checkbox is checked
    assert b.find_by_css("input[type='checkbox'][value='2'][checked='True']")

    # Do validation error by leaving username empty
    b.fill("username", "")
    b.find_by_name("save").click()
    assert b.is_text_present("There was a problem")

    # Both group checkboxes should be still selected
    assert b.find_by_css("input[type='checkbox'][value='1'][checked='True']")
    assert b.find_by_css("input[type='checkbox'][value='2'][checked='True']")



def test_remove_user_from_group(light_web_server, browser, dbsession):
    """Remove users from assigned groups in admin."""

    b = browser

    from pyramid_web20.system.user.models import Group

    create_logged_in_user(light_web_server, browser, admin=True)

    # Create a group where we
    with transaction.manager:
        g = Group(name=GROUP_NAME)
        DBSession.add(g)
        u = get_user()
        u.groups.append(g)

    b.find_by_css("#nav-admin").click()
    b.find_by_css("#btn-panel-list-user").click()
    b.find_by_css(".crud-row-1 .btn-crud-listing-edit").click()

    # Check the group checkbox. We could put some more specific classes for controls here.
    b.find_by_css("input[type='checkbox'][value='2']").click()
    b.find_by_name("save").click()

    assert b.is_text_present("Changes saved")

    # After removing we should no longer see the removed group name on user show page
    assert not b.is_text_present(GROUP_NAME)
