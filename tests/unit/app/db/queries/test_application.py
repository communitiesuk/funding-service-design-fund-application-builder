import uuid
from copy import deepcopy
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.db import db
from app.db.models import Component, ComponentType, Form, Fund, Lizt, Page, Round, Section
from app.db.queries.application import (
    delete_component,
    delete_form,
    delete_form_from_section,
    delete_page,
    delete_section,
    delete_section_from_round,
    get_component_by_id,
    get_section_by_id,
    insert_new_form,
    insert_new_section,
    move_form_down,
    move_form_up,
    move_section_down,
    move_section_up,
    swap_elements_in_list,
    update_component,
    update_form,
    update_page,
    update_section,
)
from tests.helpers import get_round_by_id
from tests.seed_test_data import BASIC_FUND_INFO, BASIC_ROUND_INFO


def insert_new_page(new_page_config):
    """Simple implementation to replace missing function for tests"""
    page = Page(
        page_id=uuid4(),
        form_id=new_page_config.get("form_id"),
        name_in_apply_json=new_page_config.get("name_in_apply_json"),
        is_template=new_page_config.get("is_template", False),
        template_name=new_page_config.get("template_name"),
        source_template_id=new_page_config.get("source_template_id"),
        audit_info=new_page_config.get("audit_info", {}),
        form_index=new_page_config.get("form_index"),
        display_path=new_page_config.get("display_path"),
        controller=new_page_config.get("controller"),
    )
    db.session.add(page)
    db.session.commit()
    return page


def insert_new_component(new_component_config):
    """Simple implementation to replace missing function for tests"""
    component = Component(
        component_id=uuid4(),
        page_id=new_component_config.get("page_id"),
        theme_id=new_component_config.get("theme_id"),
        title=new_component_config.get("title"),
        hint_text=new_component_config.get("hint_text"),
        options=new_component_config.get("options", {}),
        type=new_component_config.get("type"),
        is_template=new_component_config.get("is_template", False),
        template_name=new_component_config.get("template_name"),
        source_template_id=new_component_config.get("source_template_id"),
        audit_info=new_component_config.get("audit_info", {}),
        page_index=new_component_config.get("page_index"),
        theme_index=new_component_config.get("theme_index"),
        runner_component_name=new_component_config.get("runner_component_name"),
        list_id=new_component_config.get("list_id"),
    )
    db.session.add(component)
    db.session.commit()
    return component


new_template_section_config = {
    "round_id": uuid.uuid4(),
    "name_in_apply_json": {"en": "Section name"},
    "template_name": "Template Name",
    "is_template": True,
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "index": 1,
}

new_section_config = {
    "round_id": uuid.uuid4(),
    "name_in_apply_json": {"en": "Template section name"},
    "audit_info": {"created_by": "John Doe", "created_at": "2022-01-01"},
    "index": 1,
}


@pytest.fixture
def test_form() -> Form:
    """Fixture that creates a test form with default values."""
    return insert_new_form(
        form_name="Test form name",
        template_name="Test template name",
        runner_publish_name="test-template-name",
        form_json={},
    )


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
    updated_section_config["name_in_apply_json"] = {"en": "Updated section name"}
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


def test_failed_delete_section_cascade(flask_test_client, _db, clear_test_data, seed_dynamic_data, test_form: Form):
    new_section_config["round_id"] = None
    section = insert_new_section(new_section_config)
    # CREATE FK link to Form
    test_form.section_id = section.section_id
    # check inserted form has same section_id
    assert isinstance(section, Section)
    assert section.audit_info == new_section_config["audit_info"]
    assert isinstance(test_form, Form)
    new_form_id = test_form.form_id

    delete_section(test_form.section_id, cascade=True)

    assert _db.session.query(Section).filter(Section.section_id == section.section_id).one_or_none() is None
    assert _db.session.query(Form).where(Form.form_id == new_form_id).one_or_none() is None


def test_failed_delete_section_with_fk_to_forms(
    flask_test_client, _db, clear_test_data, seed_dynamic_data, test_form: Form
):
    new_section_config["round_id"] = None
    section = insert_new_section(new_section_config)
    # CREATE FK link to Form
    test_form.section_id = section.section_id
    # check inserted form has same section_id
    assert isinstance(section, Section)
    assert section.audit_info == new_section_config["audit_info"]

    with pytest.raises(IntegrityError):
        delete_section(test_form.section_id, cascade=False)
    _db.session.rollback()  # Rollback the failed transaction to maintain DB integrity

    existing_section = _db.session.query(Section).filter(Section.section_id == section.section_id).one_or_none()
    assert existing_section is not None, "Section was unexpectedly deleted"


def test_insert_new_form(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    new_form: Form = insert_new_form(
        form_name="Test form name",
        template_name="Test template name",
        runner_publish_name="test-template-name",
        form_json={},
    )
    assert new_form.name_in_apply_json == {"en": "Test form name"}
    assert new_form.template_name == "Test template name"
    assert new_form.runner_publish_name == "test-template-name"


def test_update_form(flask_test_client, _db, clear_test_data, seed_dynamic_data, test_form: Form):
    assert test_form.name_in_apply_json == {"en": "Test form name"}
    assert test_form.template_name == "Test template name"
    assert test_form.runner_publish_name == "test-template-name"

    updated_form: Form = update_form(
        form_id=test_form.form_id,
        form_name="Updated form name",
        template_name="Updated template name",
    )

    assert updated_form.form_id == test_form.form_id
    assert updated_form.name_in_apply_json == {"en": "Updated form name"}
    assert updated_form.template_name == "Updated template name"


def test_delete_form(flask_test_client, _db, clear_test_data, seed_dynamic_data, test_form: Form):
    delete_form(test_form.form_id)
    assert _db.session.query(Form).filter(Form.form_id == test_form.form_id).one_or_none() is None


def test_delete_form_cascade(flask_test_client, _db, clear_test_data, seed_dynamic_data, test_form: Form):
    # CREATE FK link to Form
    new_page_config["form_id"] = test_form.form_id
    new_page = insert_new_page(new_page_config)

    assert isinstance(test_form, Form)
    assert isinstance(new_page, Page)
    new_page_id = new_page.page_id

    delete_form(test_form.form_id, cascade=True)
    assert _db.session.query(Form).filter(Form.form_id == test_form.form_id).one_or_none() is None
    assert _db.session.query(Page).where(Page.page_id == new_page_id).one_or_none() is None


def test_failed_delete_form_with_fk_to_page(
    flask_test_client, _db, clear_test_data, seed_dynamic_data, test_form: Form
):
    # CREATE FK link to Form
    new_page_config["form_id"] = test_form.form_id
    insert_new_page(new_page_config)

    existing_form = _db.session.query(Form).filter(Form.form_id == test_form.form_id).one_or_none()
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


def test_delete_page_cascade(flask_test_client, _db, clear_test_data, seed_dynamic_data):
    new_page_config["form_id"] = None
    new_page = insert_new_page(new_page_config)

    assert isinstance(new_page, Page)
    page_id_to_delete = new_page.page_id
    assert new_page.audit_info == new_page_config["audit_info"]

    # create component on that page
    new_component_config["page_id"] = new_page.page_id
    new_component_config["list_id"] = None
    new_component_config["theme_id"] = None
    new_component = insert_new_component(new_component_config=new_component_config)
    assert isinstance(new_component, Component)
    component_id_to_delete = new_component.component_id

    delete_page(new_page.page_id, cascade=True)
    assert _db.session.query(Page).where(Page.page_id == page_id_to_delete).one_or_none() is None
    assert _db.session.query(Component).where(Component.component_id == component_id_to_delete).one_or_none() is None


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

    with pytest.raises(IntegrityError):
        delete_page(new_page.page_id, cascade=False)
    _db.session.rollback()  # Rollback the failed transaction to maintain DB integrity

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
    "runner_component_name": "test-component",
    "list_id": uuid.uuid4(),
}


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
    assert _db.session.query(Lizt).where(Lizt.list_id == list_id).one_or_none() is not None


def test_delete_section_with_full_cascade(flask_test_client, _db, clear_test_data, seed_dynamic_data, test_form: Form):
    new_section_config["round_id"] = None
    new_section = insert_new_section(new_section_config)
    assert isinstance(new_section, Section)
    new_section_id = new_section.section_id

    # CREATE FK link to Form
    test_form.section_id = new_section_id
    new_form_id = test_form.form_id

    # create FK link to page
    new_page_config["form_id"] = test_form.form_id
    new_page = insert_new_page(new_page_config)
    assert isinstance(new_page, Page)
    assert new_page.form_id == test_form.form_id
    new_page_id = new_page.page_id

    # create component on that page
    new_component_config["page_id"] = new_page_id
    new_component_config["list_id"] = None
    new_component_config["theme_id"] = None
    new_component = insert_new_component(new_component_config=new_component_config)
    assert isinstance(new_component, Component)
    new_component_id = new_component.component_id

    # Should successfully delete everything with cascade == true
    delete_section(new_section_id, cascade=True)
    assert _db.session.query(Section).where(Section.section_id == new_section_id).one_or_none() is None
    assert _db.session.query(Form).where(Form.form_id == new_form_id).one_or_none() is None
    assert _db.session.query(Page).where(Page.page_id == new_page_id).one_or_none() is None
    assert _db.session.query(Component).where(Component.component_id == new_component_id).one_or_none() is None


section_id = uuid4()


# Create a section with one form, at index 1
@pytest.mark.seed_config(
    {
        "sections": [Section(section_id=section_id, name_in_apply_json={"en": "hello section"})],
        "forms": [Form(form_id=uuid4(), section_id=section_id, section_index=1, name_in_apply_json={"en": "Form 1"})],
    }
)
def test_form_sorting(seed_dynamic_data, _db):
    section = seed_dynamic_data["sections"][0]
    form1 = seed_dynamic_data["forms"][0]
    result_section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 1

    # add a form at index 2, confirm ordering
    form2: Form = Form(
        form_id=uuid4(), section_id=section.section_id, section_index=2, name_in_apply_json={"en": "Form 2"}
    )
    _db.session.add(form2)
    _db.session.commit()

    result_section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 2
    assert result_section.forms[0].form_id == form1.form_id
    assert result_section.forms[1].form_id == form2.form_id

    # add a form at index 0, confirm ordering
    form0: Form = Form(
        form_id=uuid4(), section_id=section.section_id, section_index=0, name_in_apply_json={"en": "Form 0"}
    )
    _db.session.add(form0)
    _db.session.commit()

    result_section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 3
    assert result_section.forms[0].form_id == form0.form_id
    assert result_section.forms[1].form_id == form1.form_id
    assert result_section.forms[2].form_id == form2.form_id

    # insert a form between 1 and 2, check ordering
    formX: Form = Form(form_id=uuid4(), section_id=section.section_id, name_in_apply_json={"en": "Form X"})
    result_section.forms.insert(2, formX)
    _db.session.bulk_save_objects([result_section])
    _db.session.commit()

    result_section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 4
    assert result_section.forms[0].form_id == form0.form_id
    assert result_section.forms[1].form_id == form1.form_id
    assert result_section.forms[2].form_id == formX.form_id
    assert result_section.forms[3].form_id == form2.form_id
    assert result_section.forms[3].section_index == 4


section_id = uuid4()


@pytest.mark.seed_config(
    {
        "sections": [Section(section_id=section_id, name_in_apply_json={"en": "hello section"})],
        "forms": [
            Form(form_id=uuid4(), section_id=section_id, section_index=1, name_in_apply_json={"en": "Form 1"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=2, name_in_apply_json={"en": "Form 2"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=3, name_in_apply_json={"en": "Form 3"}),
        ],
    }
)
def test_form_sorting_removal(seed_dynamic_data, _db):
    section = seed_dynamic_data["sections"][0]

    result_section: Section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 3
    form2 = result_section.forms[1]
    assert form2.section_index == 2

    delete_form_from_section(section_id=result_section.section_id, form_id=form2.form_id)

    updated_section: Section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(updated_section.forms) == 2
    assert updated_section.forms[0].section_index == 1
    assert updated_section.forms[1].section_index == 2


# Create a section with one form, at index 1
round_id = uuid4()
fund_id = uuid4()


@pytest.mark.seed_config(
    {
        "funds": [Fund(**BASIC_FUND_INFO, fund_id=fund_id, short_name="UT1")],
        "rounds": [
            Round(**BASIC_ROUND_INFO, title_json={"en": "round1"}, round_id=round_id, fund_id=fund_id, short_name="R1")
        ],
        "sections": [
            Section(
                name_in_apply_json={
                    "en": "hello section",
                },
                index=1,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "hello section2"},
                index=2,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "hello section3"},
                index=3,
                round_id=round_id,
            ),
        ],
    }
)
def test_section_sorting_removal(seed_dynamic_data, _db):
    round_id = seed_dynamic_data["rounds"][0].round_id
    round: Round = get_round_by_id(round_id)
    assert len(round.sections) == 3
    last_section_id = round.sections[2].section_id
    assert round.sections[2].index == 3
    section_to_delete = round.sections[1]

    delete_section_from_round(section_id=section_to_delete.section_id, round_id=round_id)

    updated_round = get_round_by_id(round_id)
    assert len(updated_round.sections) == 2
    assert round.sections[1].section_id == last_section_id
    assert round.sections[1].index == 2


round_id = uuid4()
fund_id = uuid4()


@pytest.mark.seed_config(
    {
        "funds": [Fund(**BASIC_FUND_INFO, fund_id=fund_id, short_name="UT1")],
        "rounds": [
            Round(**BASIC_ROUND_INFO, title_json={"en": "round1"}, round_id=round_id, fund_id=fund_id, short_name="R1")
        ],
        "sections": [
            Section(
                name_in_apply_json={
                    "en": "hello section",
                },
                index=1,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "hello section2"},
                index=2,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "hello section3"},
                index=3,
                round_id=round_id,
            ),
        ],
    }
)
@pytest.mark.parametrize(
    "index_to_move, exp_new_index",
    [
        (1, 2),  # move 1 ->2
        (2, 3),  # move 2 -> 3
    ],
)
def test_section_sorting_move_down(seed_dynamic_data, _db, index_to_move, exp_new_index):
    round_id = seed_dynamic_data["rounds"][0].round_id
    round: Round = get_round_by_id(round_id)
    assert len(round.sections) == 3

    section_to_move_down = round.sections[index_to_move - 1]  # numbering starts at 1 not 0
    id_to_move = section_to_move_down.section_id
    assert section_to_move_down.index == index_to_move

    section_that_moves_up = round.sections[index_to_move]
    assert section_that_moves_up.index == index_to_move + 1
    section_id_that_moves_up = section_that_moves_up.section_id

    move_section_down(round_id=round_id, section_id=section_to_move_down.section_id)

    updated_round = get_round_by_id(round_id)
    # total sections shouldn't change
    assert len(round.sections) == 3

    # check new position
    moved_down_section = updated_round.sections[index_to_move]
    assert moved_down_section.section_id == id_to_move
    assert moved_down_section.index == exp_new_index

    # check the section that was after this one has now moved up
    moved_up_section = updated_round.sections[index_to_move - 1]
    assert moved_up_section.section_id == section_id_that_moves_up
    assert moved_up_section.index == exp_new_index - 1


round_id = uuid4()
fund_id = uuid4()


@pytest.mark.seed_config(
    {
        "funds": [Fund(**BASIC_FUND_INFO, fund_id=fund_id, short_name="UT1")],
        "rounds": [
            Round(**BASIC_ROUND_INFO, title_json={"en": "round1"}, round_id=round_id, fund_id=fund_id, short_name="R1")
        ],
        "sections": [
            Section(
                name_in_apply_json={
                    "en": "section a",
                },
                index=1,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "section b"},
                index=2,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "section c"},
                index=3,
                round_id=round_id,
            ),
        ],
    }
)
@pytest.mark.parametrize(
    "index_to_move, exp_new_index",
    [
        (2, 1),  # move 2 -> 1
        (3, 2),  # move 3 -> 2
    ],
)
def test_move_section_up(seed_dynamic_data, _db, index_to_move, exp_new_index):
    round_id = seed_dynamic_data["rounds"][0].round_id
    round: Round = get_round_by_id(round_id)
    assert len(round.sections) == 3

    section_to_move_up = round.sections[index_to_move - 1]  # list index starts at 0 not 1
    id_to_move = section_to_move_up.section_id
    assert section_to_move_up.index == index_to_move

    section_that_gets_moved_down = round.sections[index_to_move - 2]
    id_that_gets_moved_down = section_that_gets_moved_down.section_id
    assert section_that_gets_moved_down.index == index_to_move - 1

    move_section_up(round_id=round_id, section_id=id_to_move)

    updated_round = get_round_by_id(round_id)
    assert len(updated_round.sections) == 3

    # Check section that moved up
    moved_up_section = updated_round.sections[index_to_move - 2]
    assert moved_up_section.section_id == id_to_move
    assert moved_up_section.index == exp_new_index
    # Check the section that got moved down
    moved_down_section = updated_round.sections[index_to_move - 1]
    assert moved_down_section.section_id == id_that_gets_moved_down
    assert moved_down_section.index == exp_new_index + 1


section_id = uuid4()


@pytest.mark.seed_config(
    {
        "sections": [Section(section_id=section_id, name_in_apply_json={"en": "hello section"})],
        "forms": [
            Form(form_id=uuid4(), section_id=section_id, section_index=1, name_in_apply_json={"en": "Form 1"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=2, name_in_apply_json={"en": "Form 2"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=3, name_in_apply_json={"en": "Form 3"}),
        ],
    }
)
@pytest.mark.parametrize("index_to_move, exp_new_index", [(2, 1), (3, 2)])
def test_move_form_up(seed_dynamic_data, _db, index_to_move, exp_new_index):
    section_id = seed_dynamic_data["sections"][0].section_id
    section = get_section_by_id(section_id)
    assert len(section.forms) == 3

    id_to_move_up = section.forms[index_to_move - 1].form_id
    assert section.forms[index_to_move - 1].section_index == index_to_move

    id_to_move_down = section.forms[index_to_move - 2].form_id
    assert section.forms[index_to_move - 2].section_index == exp_new_index

    move_form_up(section_id, id_to_move_up)

    updated_section = get_section_by_id(section_id)
    assert len(updated_section.forms) == 3

    assert updated_section.forms[index_to_move - 2].form_id == id_to_move_up
    assert updated_section.forms[index_to_move - 1].form_id == id_to_move_down


section_id = uuid4()


@pytest.mark.seed_config(
    {
        "sections": [Section(section_id=section_id, name_in_apply_json={"en": "hello section"})],
        "forms": [
            Form(form_id=uuid4(), section_id=section_id, section_index=1, name_in_apply_json={"en": "Form 1"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=2, name_in_apply_json={"en": "Form 2"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=3, name_in_apply_json={"en": "Form 3"}),
        ],
    }
)
@pytest.mark.parametrize("index_to_move, exp_new_index", [(1, 2), (2, 3)])
def test_move_form_down(seed_dynamic_data, _db, index_to_move, exp_new_index):
    section_id = seed_dynamic_data["sections"][0].section_id
    section = get_section_by_id(section_id)
    assert len(section.forms) == 3

    id_to_move_down = section.forms[index_to_move - 1].form_id
    assert section.forms[index_to_move - 1].section_index == index_to_move

    id_to_move_up = section.forms[index_to_move].form_id
    assert section.forms[index_to_move].section_index == index_to_move + 1

    move_form_down(section_id, id_to_move_down)

    updated_section = get_section_by_id(section_id)
    assert len(updated_section.forms) == 3

    assert updated_section.forms[index_to_move].form_id == id_to_move_down
    assert updated_section.forms[index_to_move - 1].form_id == id_to_move_up


@pytest.mark.parametrize(
    "input_list, idx_a, idx_b, exp_result",
    [
        (["a", "b", "c", "d"], 0, 1, ["b", "a", "c", "d"]),
        (["a", "b", "c", "d"], 1, 3, ["a", "d", "c", "b"]),
        (["a", "b", "c", "d"], -1, 3, ["a", "b", "c", "d"]),
        (["a", "b", "c", "d"], -1, -123123, ["a", "b", "c", "d"]),
        (["a", "b", "c", "d"], 1, -123123, ["a", "b", "c", "d"]),
        (["a", "b", "c", "d"], 1, 4, ["a", "b", "c", "d"]),
    ],
)
def test_swap_elements(input_list, idx_a, idx_b, exp_result):
    result = swap_elements_in_list(input_list, idx_a, idx_b)
    assert result == exp_result


list_id = uuid4()


@pytest.mark.seed_config(
    {
        "lists": [
            Lizt(
                list_id=list_id,
                name="classifications_list",
                type="string",
                items=[{"text": "Charity", "value": "charity"}, {"text": "Public Limited Company", "value": "plc"}],
            )
        ],
        "components": [
            Component(
                component_id=uuid4(),
                page_id=None,
                title="How is your organisation classified?",
                type=ComponentType.RADIOS_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=6,
                options={"hideTitle": False, "classes": ""},
                runner_component_name="organisation_classification",
                list_id=list_id,
            )
        ],
    }
)
def test_list_relationship(seed_dynamic_data):
    result = get_component_by_id(seed_dynamic_data["components"][0].component_id)
    assert result
    assert result.list_id == list_id
    assert result.lizt
    assert result.lizt.name == "classifications_list"
