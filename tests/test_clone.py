from uuid import uuid4

import pytest

from app.blueprints.fund_builder.routes import clone_single_round
from app.db.models import Component
from app.db.models import ComponentType
from app.db.models import Page
from app.db.models.application_config import Form
from app.db.models.application_config import Section
from app.db.queries.application import _fix_cloned_default_pages
from app.db.queries.application import _initiate_cloned_component
from app.db.queries.application import _initiate_cloned_form
from app.db.queries.application import _initiate_cloned_page
from app.db.queries.application import _initiate_cloned_section
from app.db.queries.application import clone_multiple_components
from app.db.queries.application import clone_single_component
from app.db.queries.application import clone_single_form
from app.db.queries.application import clone_single_page
from app.db.queries.application import clone_single_section


@pytest.fixture
def mock_new_uuid(mocker):
    new_id = uuid4()
    mocker.patch("app.db.queries.application.uuid4", return_value=new_id)
    yield new_id


# =====================================================================================================================
# These functions test the _initiate_cloned_XXX functions and don't use the db
# =====================================================================================================================


def test_initiate_cloned_section(mock_new_uuid):
    clone: Section = Section(
        section_id="old-id",
        name_in_apply_json={"en": "test section 1"},
        round_id="old-section-id",
        is_template=True,
        template_name="Template Section",
    )
    result: Section = _initiate_cloned_section(to_clone=clone, new_round_id="new-round")
    assert result
    assert result.section_id == mock_new_uuid

    # Check other bits are the same
    assert result.name_in_apply_json == clone.name_in_apply_json

    # check template settings
    assert result.is_template is False
    assert result.source_template_id == "old-id"
    assert result.template_name is None

    assert result.round_id == "new-round"


def test_initiate_cloned_form(mock_new_uuid):
    clone: Form = Form(
        form_id="old-id",
        name_in_apply_json={"en": "test form 1"},
        section_id="old-section-id",
        is_template=True,
        template_name="Template Page",
        runner_publish_name="template-form-1",
    )
    result: Form = _initiate_cloned_form(to_clone=clone, new_section_id="new-section")
    assert result
    assert result.form_id == mock_new_uuid

    # Check other bits are the same
    assert result.name_in_apply_json == clone.name_in_apply_json
    assert result.runner_publish_name == clone.runner_publish_name

    # check template settings
    assert result.is_template is False
    assert result.source_template_id == "old-id"
    assert result.template_name is None

    assert result.section_id == "new-section"


def test_initiate_cloned_page(mock_new_uuid):
    clone: Page = Page(
        page_id="old-id",
        name_in_apply_json={"en": "test page 1"},
        form_id="old-form-id",
        is_template=True,
        template_name="Template Page",
        display_path="template-page",
    )
    result: Page = _initiate_cloned_page(to_clone=clone, new_form_id="new-form")
    assert result
    assert result.page_id == mock_new_uuid

    # Check other bits are the same
    assert result.name_in_apply_json == clone.name_in_apply_json
    assert result.display_path == clone.display_path

    # check template settings
    assert result.is_template is False
    assert result.source_template_id == "old-id"
    assert result.template_name is None

    assert result.form_id == "new-form"


def test_initiate_cloned_component(mock_new_uuid):
    clone: Component = Component(
        component_id="old-id",
        page_id="pre-clone",
        title="Template question 1?",
        type=ComponentType.TEXT_FIELD,
        template_name="Template Component",
        is_template=True,
        page_index=1,
        theme_id="pre-clone",
        theme_index=2,
        options={"hideTitle": False, "classes": "test-class"},
        runner_component_name="template_question_name",
        conditions={"a": "b"},
    )
    result = _initiate_cloned_component(clone, "page-123", "theme-234")

    assert result

    # Check new ID
    assert result.component_id == mock_new_uuid

    # Check other bits are the same
    assert result.title == clone.title
    assert result.type == clone.type
    assert result.options == clone.options
    assert result.conditions == clone.conditions

    # check template settings
    assert result.is_template is False
    assert result.source_template_id == "old-id"
    assert result.template_name is None

    assert result.page_id == "page-123"
    assert result.theme_id == "theme-234"


# =====================================================================================================================
# These functions test the clone_XXX functions and DO use the db
# =====================================================================================================================


def test_clone_single_component(flask_test_client, _db):
    template_component: Component = Component(
        component_id=uuid4(),
        page_id=None,
        title="Template question 1?",
        type=ComponentType.YES_NO_FIELD,
        page_index=1,
        theme_id=None,
        theme_index=2,
        options={"hideTitle": False, "classes": "test-class"},
        runner_component_name="template_question_name",
    )

    old_id = template_component.component_id

    _db.session.bulk_save_objects([template_component])
    _db.session.commit()

    assert _db.session.get(Component, old_id)

    result = clone_single_component(template_component.component_id)
    assert result
    new_id = result.component_id

    assert old_id != new_id

    # check can retrieve new component
    assert _db.session.get(Component, new_id)

    # Check new ID
    assert result.component_id != template_component.component_id

    # Check other bits are the same
    assert result.title == template_component.title
    assert result.type == template_component.type
    assert result.options == template_component.options
    assert result.conditions is None

    # check template settings
    assert result.is_template is False
    assert result.source_template_id == template_component.component_id

    # check can retrieve old component
    assert _db.session.get(Component, old_id)


page_id = uuid4()


@pytest.mark.seed_config(
    {
        "components": [
            Component(
                component_id=uuid4(),
                page_id=None,
                title="Template question 1?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_1",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=None,
                title="Template question 2?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_2",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=None,
                title="Template question 3?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_3",
                is_template=True,
            ),
        ],
    }
)
def test_clone_multiple_components(seed_dynamic_data, _db):
    existing_components = seed_dynamic_data["components"]

    results = clone_multiple_components(
        component_ids=[c.component_id for c in existing_components],
        new_page_id=None,
        new_theme_id=None,
    )
    assert results
    assert len(results) == 3

    # Check new component exists in db
    from_db = _db.session.query(Component).filter(Component.component_id.in_([c.component_id for c in results])).all()
    assert from_db
    assert len(from_db) == 3

    # Check the old ones exist
    from_db = (
        _db.session.query(Component)
        .filter(Component.component_id.in_([c.component_id for c in existing_components]))
        .all()
    )
    assert from_db
    assert len(from_db) == 3


@pytest.mark.seed_config(
    {
        "pages": [
            Page(
                page_id=uuid4(),
                form_id=None,
                display_path="testing-clones-no-components",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            )
        ]
    }
)
def test_clone_page_no_components(seed_dynamic_data, _db):

    old_id = seed_dynamic_data["pages"][0].page_id

    # check initial page exists
    initial_page_from_db = _db.session.query(Page).where(Page.page_id == old_id).one_or_none()
    assert initial_page_from_db

    result = clone_single_page(page_id=old_id, new_form_id=None)
    assert result
    new_id = result.page_id

    assert old_id != new_id

    # check new page exists
    new_page_from_db = _db.session.query(Page).where(Page.page_id == new_id).one_or_none()
    assert new_page_from_db

    # check old page still exists
    old_page_from_db = _db.session.query(Page).where(Page.page_id == old_id).one_or_none()
    assert old_page_from_db


page_id = uuid4()


def test_fix_clone_default_pages():

    original_pages = [
        Page(page_id=uuid4(), is_template=True),
        Page(page_id=uuid4(), is_template=True),
        Page(page_id=uuid4(), is_template=True),
        Page(page_id=uuid4(), is_template=True),
    ]

    cloned_pages = [
        Page(
            page_id=uuid4(),
            is_template=False,
            source_template_id=original_pages[0].page_id,
            default_next_page_id=original_pages[1].page_id,
        ),
        Page(
            page_id=uuid4(),
            is_template=False,
            source_template_id=original_pages[1].page_id,
            default_next_page_id=original_pages[2].page_id,
        ),
        Page(
            page_id=uuid4(),
            is_template=False,
            source_template_id=original_pages[2].page_id,
            default_next_page_id=original_pages[3].page_id,
        ),
        Page(
            page_id=uuid4(), is_template=False, source_template_id=original_pages[3].page_id, default_next_page_id=None
        ),
    ]

    results = _fix_cloned_default_pages(cloned_pages)
    assert results[0].default_next_page_id == results[1].page_id
    assert results[1].default_next_page_id == results[2].page_id
    assert results[2].default_next_page_id == results[3].page_id
    assert results[3].default_next_page_id is None


@pytest.mark.seed_config(
    {
        "pages": [
            Page(
                page_id=page_id,
                form_id=None,
                display_path="testing-clones-with-components",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            )
        ],
        "components": [
            Component(
                component_id=uuid4(),
                page_id=page_id,
                title="Template question 1?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_1",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=page_id,
                title="Template question 2?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_2",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=page_id,
                title="Template question 3?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_3",
                is_template=True,
            ),
        ],
    }
)
def test_clone_page_with_components(seed_dynamic_data, _db):

    old_page_id = seed_dynamic_data["pages"][0].page_id
    old_component_ids = [str(c.component_id) for c in seed_dynamic_data["components"]]

    # check initial page exists
    initial_page_from_db = _db.session.query(Page).where(Page.page_id == old_page_id).one_or_none()
    assert initial_page_from_db

    result = clone_single_page(page_id=old_page_id, new_form_id=None)
    assert result
    new_id = result.page_id

    assert old_page_id != new_id

    # check new page exists
    new_page_from_db = _db.session.query(Page).where(Page.page_id == new_id).one_or_none()
    assert new_page_from_db
    # check components have also been cloned
    assert len(new_page_from_db.components) == 3
    for component in new_page_from_db.components:
        assert str(component.component_id) not in old_component_ids

    # check old page still exists
    old_page_from_db = _db.session.query(Page).where(Page.page_id == old_page_id).one_or_none()
    assert old_page_from_db
    # check old page still has references to original components
    assert len(old_page_from_db.components) == 3
    for component in old_page_from_db.components:
        assert str(component.component_id) in old_component_ids


@pytest.mark.seed_config(
    {
        "forms": [
            Form(
                form_id=uuid4(),
                section_id=None,
                name_in_apply_json={"en": "UT Form 1"},
                section_index=2,
                runner_publish_name="ut-form-1",
            )
        ]
    }
)
def test_clone_form_no_pages(seed_dynamic_data, _db):
    old_form = _db.session.get(Form, seed_dynamic_data["forms"][0].form_id)
    assert old_form

    result = clone_single_form(form_id=old_form.form_id, new_section_id=None)
    assert result
    assert result.form_id != old_form.form_id

    cloned_form = _db.session.get(Form, result.form_id)
    assert cloned_form
    assert len(cloned_form.pages) == 0

    old_form_from_db = _db.session.get(Form, old_form.form_id)
    assert old_form_from_db


form_id_2 = uuid4()


@pytest.mark.seed_config(
    {
        "forms": [
            Form(
                form_id=form_id_2,
                section_id=None,
                name_in_apply_json={"en": "UT Form 2"},
                section_index=2,
                runner_publish_name="ut-form-2",
            )
        ],
        "pages": [
            Page(
                page_id=uuid4(),
                form_id=form_id_2,
                display_path="testing-clone-from-form",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            )
        ],
    }
)
def test_clone_form_with_page(seed_dynamic_data, _db):
    old_form = _db.session.get(Form, seed_dynamic_data["forms"][0].form_id)
    assert old_form

    result = clone_single_form(form_id=old_form.form_id, new_section_id=None)
    assert result
    assert result.form_id != old_form.form_id

    cloned_form = _db.session.get(Form, result.form_id)
    assert cloned_form
    assert len(cloned_form.pages) == 1
    new_page_id = cloned_form.pages[0].page_id
    assert cloned_form.pages[0].form_id == result.form_id

    old_form_from_db = _db.session.get(Form, old_form.form_id)
    assert old_form_from_db
    assert len(old_form_from_db.pages) == 1
    old_page_id = old_form_from_db.pages[0].page_id

    assert old_page_id != new_page_id


form_id_3 = uuid4()
page_id_2 = uuid4()
page_id_3 = uuid4()


@pytest.mark.seed_config(
    {
        "forms": [
            Form(
                form_id=form_id_3,
                section_id=None,
                name_in_apply_json={"en": "UT Form 2"},
                section_index=2,
                runner_publish_name="ut-form-2",
            )
        ],
        "pages": [
            Page(
                page_id=page_id_2,
                form_id=form_id_3,
                display_path="testing-clone-from-form-2",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            ),
            Page(
                page_id=page_id_3,
                form_id=form_id_3,
                display_path="testing-clone-from-form-3",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            ),
        ],
        "components": [
            Component(
                component_id=uuid4(),
                page_id=page_id_2,
                title="Template question 1?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_1",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=page_id_2,
                title="Template question 2?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_2",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=page_id_3,
                title="Template question 3?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_3",
                is_template=True,
            ),
        ],
    }
)
def test_clone_form_with_pages_and_components(seed_dynamic_data, _db):
    old_form = _db.session.get(Form, seed_dynamic_data["forms"][0].form_id)
    assert old_form

    result = clone_single_form(form_id=old_form.form_id, new_section_id=None)
    assert result
    assert result.form_id != old_form.form_id

    cloned_form = _db.session.get(Form, result.form_id)
    assert cloned_form
    assert len(cloned_form.pages) == 2
    new_page_id_1 = next(p.page_id for p in cloned_form.pages if p.display_path == "testing-clone-from-form-2")
    new_page_id_2 = next(p.page_id for p in cloned_form.pages if p.display_path == "testing-clone-from-form-3")
    new_page_1: Page = _db.session.get(Page, new_page_id_1)
    new_page_2: Page = _db.session.get(Page, new_page_id_2)

    old_form_from_db = _db.session.get(Form, old_form.form_id)
    assert old_form_from_db
    assert len(old_form_from_db.pages) == 2

    # Set old page id 1 and 2 to be the ids of the old pages that correspond to the new
    # pages 1 and 2 by matching display path
    old_page_id_1 = next(p.page_id for p in old_form_from_db.pages if p.display_path == new_page_1.display_path)
    old_page_id_2 = next(p.page_id for p in old_form_from_db.pages if p.display_path == new_page_2.display_path)

    assert new_page_id_1 not in [old_page_id_1, old_page_id_2]
    assert new_page_id_2 not in [old_page_id_1, old_page_id_2]

    # Check pages and components

    assert len(new_page_1.components) == 2
    assert len(new_page_2.components) == 1

    old_page_1 = _db.session.get(Page, old_page_id_1)
    old_page_2 = _db.session.get(Page, old_page_id_2)

    old_component_ids_1 = [c.component_id for c in old_page_1.components]
    old_component_ids_2 = [c.component_id for c in old_page_2.components]

    # check the new components are different than the old ones
    assert new_page_1.components[0].component_id not in old_component_ids_1
    assert new_page_1.components[1].component_id not in old_component_ids_1
    assert new_page_2.components[0].component_id not in old_component_ids_2


@pytest.mark.seed_config(
    {
        "sections": [
            Section(
                section_id=uuid4(),
                name_in_apply_json={"en": "UT Section 1"},
                index=2,
            )
        ]
    }
)
def test_clone_section_no_forms(seed_dynamic_data, _db):
    old_section = _db.session.get(Section, seed_dynamic_data["sections"][0].section_id)
    assert old_section

    result = clone_single_section(section_id=old_section.section_id, new_round_id=None)
    assert result
    assert result.section_id != old_section.section_id

    cloned_section = _db.session.get(Section, result.section_id)
    assert cloned_section
    assert len(cloned_section.forms) == 0

    old_section_from_db = _db.session.get(Section, old_section.section_id)
    assert old_section_from_db


section_id_to_clone = uuid4()
form_id_to_clone = uuid4()
page_id_to_clone_1 = uuid4()
page_id_to_clone_2 = uuid4()


@pytest.mark.seed_config(
    {
        "sections": [
            Section(
                section_id=section_id_to_clone,
                name_in_apply_json={"en": "UT Section 2"},
                index=2,
            )
        ],
        "forms": [
            Form(
                form_id=form_id_to_clone,
                section_id=section_id_to_clone,
                name_in_apply_json={"en": "UT Form 2"},
                section_index=2,
                runner_publish_name="ut-form-2",
            )
        ],
        "pages": [
            Page(
                page_id=page_id_to_clone_1,
                form_id=form_id_to_clone,
                display_path="testing-clone-from-section-1",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            ),
            Page(
                page_id=page_id_to_clone_2,
                form_id=form_id_to_clone,
                display_path="testing-clone-from-section-2",
                is_template=True,
                name_in_apply_json={"en": "Clone testing"},
                form_index=0,
            ),
        ],
        "components": [
            Component(
                component_id=uuid4(),
                page_id=page_id_to_clone_1,
                title="Template question 1?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_1",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=page_id_to_clone_1,
                title="Template question 2?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_2",
                is_template=True,
            ),
            Component(
                component_id=uuid4(),
                page_id=page_id_to_clone_2,
                title="Template question 3?",
                type=ComponentType.YES_NO_FIELD,
                page_index=1,
                theme_id=None,
                theme_index=2,
                options={"hideTitle": False, "classes": "test-class"},
                runner_component_name="template_question_name_3",
                is_template=True,
            ),
        ],
    }
)
def test_clone_section_with_forms(seed_dynamic_data, _db):
    old_section = _db.session.get(Section, seed_dynamic_data["sections"][0].section_id)
    assert old_section

    result = clone_single_section(section_id=old_section.section_id, new_round_id=None)
    assert result
    assert result.section_id != old_section.section_id

    cloned_section = _db.session.get(Section, result.section_id)
    assert cloned_section
    assert len(cloned_section.forms) == 1

    # check the old section still exists
    old_section_from_db = _db.session.get(Section, old_section.section_id)
    assert old_section_from_db

    # validate the form
    cloned_form = _db.session.get(Form, cloned_section.forms[0].form_id)
    assert cloned_form
    assert len(cloned_form.pages) == 2
    new_page_id_1 = next(p.page_id for p in cloned_form.pages if p.display_path == "testing-clone-from-section-1")
    new_page_id_2 = next(p.page_id for p in cloned_form.pages if p.display_path == "testing-clone-from-section-2")
    new_page_1: Page = _db.session.get(Page, new_page_id_1)
    new_page_2: Page = _db.session.get(Page, new_page_id_2)

    old_form_from_db = _db.session.get(Form, seed_dynamic_data["forms"][0].form_id)
    assert old_form_from_db
    assert len(old_form_from_db.pages) == 2

    # Set old page id 1 and 2 to be the ids of the old pages that correspond to the new
    # pages 1 and 2 by matching display path
    old_page_id_1 = next(p.page_id for p in old_form_from_db.pages if p.display_path == new_page_1.display_path)
    old_page_id_2 = next(p.page_id for p in old_form_from_db.pages if p.display_path == new_page_2.display_path)

    assert new_page_id_1 not in [old_page_id_1, old_page_id_2]
    assert new_page_id_2 not in [old_page_id_1, old_page_id_2]

    # Check pages and components

    assert len(new_page_1.components) == 2
    assert len(new_page_2.components) == 1

    old_page_1 = _db.session.get(Page, old_page_id_1)
    old_page_2 = _db.session.get(Page, old_page_id_2)

    old_component_ids_1 = [c.component_id for c in old_page_1.components]
    old_component_ids_2 = [c.component_id for c in old_page_2.components]

    # check the new components are different than the old ones
    assert new_page_1.components[0].component_id not in old_component_ids_1
    assert new_page_1.components[1].component_id not in old_component_ids_1
    assert new_page_2.components[0].component_id not in old_component_ids_2


def test_clone_round(seed_dynamic_data, _db):
    # find seeded round id
    fund = seed_dynamic_data["funds"][0]
    round_id = seed_dynamic_data["rounds"][0].round_id
    old_section_ids = [s.section_id for s in seed_dynamic_data["sections"]]
    old_form_ids = [f.form_id for f in seed_dynamic_data["forms"]]
    old_page_ids = [p.page_id for p in seed_dynamic_data["pages"]]

    # add a second page so we can check updates of default_next_page_id
    p2: Page = Page(
        page_id=uuid4(),
        form_id=old_form_ids[0],
        display_path="second-page",
        name_in_apply_json={"en": "Second Page"},
        form_index=2,
        default_next_page_id=old_page_ids[0],
    )
    _db.session.add(p2)
    _db.session.commit()
    old_page_ids.append(p2.page_id)

    old_component_ids = [c.component_id for c in seed_dynamic_data["components"]]
    assert len(old_section_ids) > 0, "Need at least one section to clone"
    assert len(old_form_ids) > 0, "Need at least one form to clone"
    assert len(old_page_ids) > 1, "Need at least two pages to clone"
    assert len(old_component_ids) > 0, "Need at least one component to clone"

    cloned_round = clone_single_round(round_id, fund.fund_id, fund.short_name)
    cloned_sections = _db.session.query(Section).filter(Section.round_id == cloned_round.round_id).all()
    cloned_section_ids = [s.section_id for s in cloned_sections]
    cloned_forms = _db.session.query(Form).filter(Form.section_id.in_(cloned_section_ids)).all()
    cloned_form_ids = [f.form_id for f in cloned_forms]
    cloned_pages: list[Page] = _db.session.query(Page).filter(Page.form_id.in_(cloned_form_ids)).all()
    cloned_page_ids = [p.page_id for p in cloned_pages]

    # assert cloned_round is different
    assert cloned_round.round_id != round_id

    # assert cloned sections are different (ids)
    assert len(cloned_sections) == len(old_section_ids)
    assert all([s.section_id != old_id for s, old_id in zip(cloned_sections, old_section_ids)])

    # assert cloned forms are different (ids)
    assert len(cloned_forms) == len(old_form_ids)
    assert all([f.form_id != old_id for f, old_id in zip(cloned_forms, old_form_ids)])

    # assert cloned pages are different (ids)
    assert len(cloned_pages) == len(old_page_ids)
    assert all([p.page_id != old_id for p, old_id in zip(cloned_pages, old_page_ids)])
    for p in cloned_pages:
        assert p.default_next_page_id not in old_page_ids

    # assert cloned components are different (ids)
    cloned_components = _db.session.query(Component).filter(Component.page_id.in_(cloned_page_ids)).all()
    assert all([c.component_id != old_id for c, old_id in zip(cloned_components, old_component_ids)])
