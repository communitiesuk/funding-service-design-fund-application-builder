import uuid
from copy import deepcopy

from sqlalchemy.exc import IntegrityError

from app.db.models import ComponentType
from app.db.models.application_config import Component
from app.db.models.application_config import Form
from app.db.models.application_config import Page
from app.db.models.application_config import Section
from app.db.queries.application import delete_component
from app.db.queries.application import delete_form
from app.db.queries.application import delete_page
from app.db.queries.application import delete_section
from app.db.queries.application import insert_new_component
from app.db.queries.application import insert_new_form
from app.db.queries.application import insert_new_page
from app.db.queries.application import insert_new_section
from app.db.queries.application import update_component
from app.db.queries.application import update_form
from app.db.queries.application import update_page
from app.db.queries.application import update_section

new_template_section_config = {
    "round_id": uuid.uuid4(),
    "name_in_apply_json": {"en": "Section Name"},
    "template_name": "Template Name",
    "is_template": True,
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "index": 1,
}

new_section_config = {
    "round_id": uuid.uuid4(),
    "name_in_apply_json": {"en": "Template Section Name"},
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "index": 1,
}


def test_insert_new_section(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    # Access actual round_id from seed_dynamic_data (could also be None)
    round_id = seed_dynamic_data["rounds"][0].round_id

    # Update the configs with the round_id
    new_template_section_config["round_id"] = round_id
    new_section_config["round_id"] = round_id

    new_section = insert_new_section(new_section_config)
    template_section = insert_new_section(new_template_section_config)

    assert isinstance(template_section, Section)
    assert template_section.round_id == new_template_section_config["round_id"]
    assert template_section.name_in_apply_json == new_template_section_config["name_in_apply_json"]
    assert template_section.template_name == new_template_section_config["template_name"]
    assert template_section.is_template is True
    assert new_section.source_template_id is None
    assert template_section.audit_info == new_template_section_config["audit_info"]
    assert template_section.index == new_template_section_config["index"]

    assert isinstance(new_section, Section)
    assert new_section.round_id == new_section_config["round_id"]
    assert new_section.name_in_apply_json == new_section_config["name_in_apply_json"]
    assert new_section.template_name is None
    assert new_section.is_template is False
    assert new_section.source_template_id is None
    assert new_section.audit_info == new_section_config["audit_info"]
    assert new_section.index == new_section_config["index"]


def test_update_section(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    round_id = seed_dynamic_data["rounds"][0].round_id
    new_section_config["round_id"] = round_id
    new_section = insert_new_section(new_section_config)

    assert new_section.round_id == new_section_config["round_id"]
    assert new_section.name_in_apply_json == new_section_config["name_in_apply_json"]
    assert new_section.template_name is None
    assert new_section.is_template is False
    assert new_section.source_template_id is None
    assert new_section.audit_info == new_section_config["audit_info"]
    assert new_section.index == new_section_config["index"]

    # Update new_section_config
    updated_section_config = deepcopy(new_section_config)
    updated_section_config["name_in_apply_json"] = {"en": "Updated Section Name"}
    updated_section_config["audit_info"] = {"created_by": "Jonny Doe", "created_at": "2024-01-02"}

    updated_section = update_section(new_section.section_id, updated_section_config)
    # write assertions for updated_section
    assert isinstance(updated_section, Section)
    assert updated_section.round_id == updated_section_config["round_id"]
    assert updated_section.name_in_apply_json == updated_section_config["name_in_apply_json"]
    assert updated_section.audit_info == updated_section_config["audit_info"]


def test_delete_section(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    round_id = seed_dynamic_data["rounds"][0].round_id
    new_section_config["round_id"] = round_id
    new_section = insert_new_section(new_section_config)

    assert isinstance(new_section, Section)
    assert new_section.audit_info == new_section_config["audit_info"]

    delete_section(new_section.section_id)
    assert _db.session.query(Section).filter(Section.section_id == new_section.section_id).one_or_none() is None


def test_failed_delete_section_with_fk_to_forms(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    new_section_config["round_id"] = None
    section = insert_new_section(new_section_config)
    # CREATE FK link to Form
    new_form_config["section_id"] = section.section_id
    form = insert_new_form(new_form_config)
    # check inserted form has same section_id
    assert form.section_id == section.section_id
    assert isinstance(section, Section)
    assert section.audit_info == new_section_config["audit_info"]

    try:
        delete_section(form.section_id)
        assert False, "Expected IntegrityError was not raised"
    except IntegrityError:
        _db.session.rollback()  # Rollback the failed transaction to maintain DB integrity
        assert True  # Explicitly pass the test to indicate the expected error was caught

    existing_section = _db.session.query(Section).filter(Section.section_id == section.section_id).one_or_none()
    assert existing_section is not None, "Section was unexpectedly deleted"


new_form_config = {
    "section_id": uuid.uuid4(),
    "name_in_apply_json": {"en": "Form Name"},
    "is_template": False,
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "section_index": 1,
    "runner_publish_name": "test-form",
}

new_template_form_config = {
    "section_id": uuid.uuid4(),
    "name_in_apply_json": {"en": "Template Form Name"},
    "template_name": "Form Template Name",
    "is_template": True,
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "section_index": 1,
    "runner_publish_name": None,  # This is a template
}


def test_insert_new_form(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    round_id = seed_dynamic_data["rounds"][0].round_id
    new_section_config["round_id"] = round_id
    new_section = insert_new_section(new_section_config)
    # Point to a section that exists in the db
    new_form_config["section_id"] = new_section.section_id  # *Does not need to belong to a section
    new_template_form_config["section_id"] = new_section.section_id  # *Does not need to belong to a section

    new_template_form = insert_new_form(new_template_form_config)
    assert isinstance(new_template_form, Form)
    assert new_template_form.section_id == new_template_form_config["section_id"]
    assert new_template_form.name_in_apply_json == new_template_form_config["name_in_apply_json"]
    assert new_template_form.template_name == new_template_form_config["template_name"]
    assert new_template_form.is_template is True
    assert new_template_form.source_template_id is None
    assert new_template_form.audit_info == new_template_form_config["audit_info"]
    assert new_template_form.section_index == new_template_form_config["section_index"]
    assert new_template_form.runner_publish_name is None

    new_form = insert_new_form(new_form_config)
    assert isinstance(new_form, Form)
    assert new_form.section_id == new_form_config["section_id"]
    assert new_form.name_in_apply_json == new_form_config["name_in_apply_json"]
    assert new_form.template_name is None
    assert new_form.source_template_id is None  # not cloned, its a new non-template form
    assert new_form.is_template is False
    assert new_form.audit_info == new_form_config["audit_info"]
    assert new_form.section_index == new_form_config["section_index"]
    assert new_form.runner_publish_name == new_form_config["runner_publish_name"]

    new_form_config["section_index"] = 2
    new_form = insert_new_form(new_form_config)
    assert new_form.section_index == new_form_config["section_index"]


def test_update_form(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    round_id = seed_dynamic_data["rounds"][0].round_id
    new_section_config["round_id"] = round_id
    new_section = insert_new_section(new_section_config)
    new_form_config["section_id"] = new_section.section_id
    new_form = insert_new_form(new_form_config)

    assert new_form.section_id == new_form_config["section_id"]
    assert new_form.name_in_apply_json == new_form_config["name_in_apply_json"]
    assert new_form.template_name is None
    assert new_form.is_template is False
    assert new_form.source_template_id is None
    assert new_form.audit_info == new_form_config["audit_info"]
    assert new_form.section_index == new_form_config["section_index"]
    assert new_form.runner_publish_name == new_form_config["runner_publish_name"]

    # Update new_form_config
    updated_form_config = deepcopy(new_form_config)
    updated_form_config["name_in_apply_json"] = {"en": "Updated Form Name"}
    updated_form_config["audit_info"] = {"created_by": "Jonny Doe", "created_at": "2024-01-02"}

    updated_form = update_form(new_form.form_id, updated_form_config)

    assert isinstance(updated_form, Form)
    assert updated_form.section_id == updated_form_config["section_id"]
    assert updated_form.name_in_apply_json == updated_form_config["name_in_apply_json"]
    assert updated_form.audit_info == updated_form_config["audit_info"]


def test_delete_form(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    round_id = seed_dynamic_data["rounds"][0].round_id
    new_section_config["round_id"] = round_id
    new_section = insert_new_section(new_section_config)
    new_form_config["section_id"] = new_section.section_id
    new_form = insert_new_form(new_form_config)

    assert isinstance(new_form, Form)
    assert new_form.audit_info == new_form_config["audit_info"]

    delete_form(new_form.form_id)
    assert _db.session.query(Form).filter(Form.form_id == new_form.form_id).one_or_none() is None


def test_failed_delete_form_with_fk_to_page(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    new_form_config["section_id"] = None
    form = insert_new_form(new_form_config)
    # CREATE FK link to Form
    new_page_config["form_id"] = form.form_id
    page = insert_new_page(new_page_config)

    try:
        delete_form(page.form_id)
        assert False, "Expected IntegrityError was not raised"
    except IntegrityError:
        _db.session.rollback()  # Rollback the failed transaction to maintain DB integrity
        assert True  # Explicitly pass the test to indicate the expected error was caught

    existing_form = _db.session.query(Form).filter(Form.form_id == form.form_id).one_or_none()
    assert existing_form is not None, "Form was unexpectedly deleted"


new_page_config = {
    "form_id": uuid.uuid4(),
    "name_in_apply_json": {"en": "Page Name"},
    "is_template": False,
    "template_name": None,
    "source_template_id": None,
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "form_index": 1,
    "display_path": "test-page",
    "controller": "./test-controller",
}

new_template_page_config = {
    "form_id": uuid.uuid4(),
    "name_in_apply_json": {"en": "Template Page Name"},
    "is_template": True,
    "template_name": "Page Template Name",
    "source_template_id": None,
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "form_index": 1,
    "display_path": "test-page",
    "controller": None,
}


def test_insert_new_page(flask_test_client, _db, clear_test_data, seed_dynamic_data):

    new_form_config["section_id"] = None
    new_form = insert_new_form(new_form_config)

    new_page_config["form_id"] = new_form.form_id  # *Does not need to belong to a form
    new_template_page_config["form_id"] = None  # *Does not need to belong to a form

    new_template_page = insert_new_page(new_template_page_config)
    assert isinstance(new_template_page, Page)
    assert new_template_page.form_id is None
    assert new_template_page.name_in_apply_json == new_template_page_config["name_in_apply_json"]
    assert new_template_page.template_name == new_template_page_config["template_name"]
    assert new_template_page.is_template is True
    assert new_template_page.source_template_id is None
    assert new_template_page.audit_info == new_template_page_config["audit_info"]
    assert new_template_page.form_index == new_template_page_config["form_index"]
    assert new_template_page.display_path == new_page_config["display_path"]
    assert new_template_page.controller == new_template_page_config["controller"]

    new_page = insert_new_page(new_page_config)
    assert isinstance(new_page, Page)
    assert new_page.form_id == new_page_config["form_id"]
    assert new_page.name_in_apply_json == new_page_config["name_in_apply_json"]
    assert new_page.template_name is None
    assert new_page.is_template is False
    assert new_page.source_template_id is None
    assert new_page.audit_info == new_page_config["audit_info"]
    assert new_page.form_index == new_page_config["form_index"]
    assert new_page.display_path == new_page_config["display_path"]
    assert new_page.controller == new_page_config["controller"]


def test_update_page(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    new_page_config["form_id"] = None
    new_page = insert_new_page(new_page_config)

    assert new_page.form_id is None
    assert new_page.name_in_apply_json == new_page_config["name_in_apply_json"]
    assert new_page.template_name is None
    assert new_page.is_template is False
    assert new_page.source_template_id is None
    assert new_page.audit_info == new_page_config["audit_info"]
    assert new_page.form_index == new_page_config["form_index"]
    assert new_page.display_path == new_page_config["display_path"]
    assert new_page.controller == new_page_config["controller"]

    # Update new_page_config
    updated_page_config = deepcopy(new_page_config)
    updated_page_config["name_in_apply_json"] = {"en": "Updated Page Name"}
    updated_page_config["audit_info"] = {"created_by": "Jonny Doe", "created_at": "2024-01-02"}

    updated_page = update_page(new_page.page_id, updated_page_config)

    assert isinstance(updated_page, Page)
    assert updated_page.form_id == updated_page_config["form_id"]
    assert updated_page.name_in_apply_json == updated_page_config["name_in_apply_json"]
    assert updated_page.audit_info == updated_page_config["audit_info"]


def test_delete_page(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    new_page_config["form_id"] = None
    new_page = insert_new_page(new_page_config)

    assert isinstance(new_page, Page)
    assert new_page.audit_info == new_page_config["audit_info"]

    delete_page(new_page.page_id)
    assert _db.session.query(Page).filter(Page.page_id == new_page.page_id).one_or_none() is None


def test_failed_delete_page_with_fk_to_component(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    new_page_config["form_id"] = None
    new_page = insert_new_page(new_page_config)
    # CREATE FK link to Component
    new_component_config["page_id"] = new_page.page_id
    new_component_config["list_id"] = None
    new_component_config["theme_id"] = None
    component = insert_new_component(new_component_config)
    # check inserted component has same page_id
    assert component.page_id == new_page.page_id
    assert isinstance(new_page, Page)
    assert new_page.audit_info == new_page_config["audit_info"]

    try:
        delete_page(component.page_id)
        assert False, "Expected IntegrityError was not raised"
    except IntegrityError:
        _db.session.rollback()  # Rollback the failed transaction to maintain DB integrity
        assert True  # Explicitly pass the test to indicate the expected error was caught

    existing_page = _db.session.query(Page).filter(Page.page_id == new_page.page_id).one_or_none()
    assert existing_page is not None, "Page was unexpectedly deleted"


new_component_config = {
    "page_id": uuid.uuid4(),
    "theme_id": uuid.uuid4(),
    "title": "Component Title",
    "hint_text": "Component Hint Text",
    "options": {"hideTitle": False, "classes": "test-class"},
    "type": ComponentType.TEXT_FIELD,
    "is_template": False,
    "template_name": None,
    "source_template_id": None,
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "page_index": 1,
    "theme_index": 1,
    "conditions": [
        {
            "name": "organisation_other_names_no",
            "value": "false",  # this must be lowercaes or the navigation doesn't work
            "operator": "is",
            "destination_page_path": "CONTINUE",
        },
        {
            "name": "organisation_other_names_yes",
            "value": "true",  # this must be lowercaes or the navigation doesn't work
            "operator": "is",
            "destination_page_path": "organisation-alternative-names",
        },
    ],
    "runner_component_name": "test-component",
    "list_id": uuid.uuid4(),
}


new_template_component_config = {
    "page_id": uuid.uuid4(),
    "theme_id": uuid.uuid4(),
    "title": "Template Component Title",
    "hint_text": "Template Component Hint Text",
    "options": {"hideTitle": False, "classes": "test-class"},
    "type": ComponentType.TEXT_FIELD,
    "is_template": True,
    "template_name": "Component Template Name",
    "source_template_id": None,
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "page_index": 1,
    "theme_index": 2,
    "conditions": [
        {
            "name": "path_start_no",
            "value": "false",  # this must be lowercaes or the navigation doesn't work
            "operator": "is",
            "destination_page_path": "path-1",
        },
        {
            "name": "path_start_yes",
            "value": "true",  # this must be lowercaes or the navigation doesn't work
            "operator": "is",
            "destination_page_path": "path-2",
        },
    ],
    "runner_component_name": "test-component",
    "list_id": uuid.uuid4(),
}


def test_insert_new_component(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    page_id = seed_dynamic_data["pages"][0].page_id
    list_id = seed_dynamic_data["lists"][0].list_id
    theme_id = seed_dynamic_data["themes"][0].theme_id
    new_component_config["page_id"] = page_id
    new_template_component_config["page_id"] = None
    new_component_config["list_id"] = list_id
    new_template_component_config["list_id"] = list_id
    new_component_config["theme_id"] = theme_id
    new_template_component_config["theme_id"] = theme_id

    component = insert_new_component(new_component_config)
    assert isinstance(component, Component)
    assert component.page_id == new_component_config["page_id"]
    assert component.theme_id == new_component_config["theme_id"]
    assert component.title == new_component_config["title"]
    assert component.hint_text == new_component_config["hint_text"]
    assert component.options == new_component_config["options"]
    assert component.type == new_component_config["type"]
    assert component.is_template is False
    assert component.template_name is None
    assert component.source_template_id is None
    assert component.audit_info == new_component_config["audit_info"]
    assert component.page_index == new_component_config["page_index"]
    assert component.theme_index == new_component_config["theme_index"]
    assert component.conditions == new_component_config["conditions"]
    assert component.runner_component_name == new_component_config["runner_component_name"]
    assert component.list_id == new_component_config["list_id"]

    template_component = insert_new_component(new_template_component_config)
    assert isinstance(template_component, Component)
    assert template_component.page_id is None
    assert template_component.theme_id == new_template_component_config["theme_id"]
    assert template_component.title == new_template_component_config["title"]
    assert template_component.hint_text == new_template_component_config["hint_text"]
    assert template_component.options == new_template_component_config["options"]
    assert template_component.type == new_template_component_config["type"]
    assert template_component.is_template is True
    assert template_component.template_name == new_template_component_config["template_name"]
    assert template_component.source_template_id is None
    assert template_component.audit_info == new_template_component_config["audit_info"]
    assert template_component.page_index == new_template_component_config["page_index"]
    assert template_component.theme_index == new_template_component_config["theme_index"]
    assert template_component.conditions == new_template_component_config["conditions"]
    assert template_component.runner_component_name == new_template_component_config["runner_component_name"]
    assert template_component.list_id == new_template_component_config["list_id"]


def test_update_component(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    page_id = seed_dynamic_data["pages"][0].page_id
    list_id = seed_dynamic_data["lists"][0].list_id
    theme_id = seed_dynamic_data["themes"][0].theme_id
    new_component_config["page_id"] = page_id
    new_component_config["list_id"] = list_id
    new_component_config["theme_id"] = theme_id

    component = insert_new_component(new_component_config)

    assert component.title == new_component_config["title"]
    assert component.audit_info == new_component_config["audit_info"]
    assert component.is_template is False

    # Update new_component_config
    updated_component_config = deepcopy(new_component_config)
    updated_component_config["title"] = "Updated Component Title"
    updated_component_config["audit_info"] = {"created_by": "Adam Doe", "created_at": "2024-01-02"}

    updated_component = update_component(component.component_id, updated_component_config)

    assert isinstance(updated_component, Component)
    assert updated_component.title == updated_component_config["title"]
    assert updated_component.audit_info == updated_component_config["audit_info"]
    assert updated_component.is_template is False


def test_delete_component(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    page_id = seed_dynamic_data["pages"][0].page_id
    list_id = seed_dynamic_data["lists"][0].list_id
    theme_id = seed_dynamic_data["themes"][0].theme_id
    new_component_config["page_id"] = page_id
    new_component_config["list_id"] = list_id
    new_component_config["theme_id"] = theme_id

    component = insert_new_component(new_component_config)

    assert isinstance(component, Component)
    assert component.audit_info == new_component_config["audit_info"]

    delete_component(component.component_id)
    assert _db.session.query(Component).filter(Component.component_id == component.component_id).one_or_none() is None
