import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.db.models import Component, Form, FormSection, Lizt, Page
from app.db.models.application_config import ComponentType
from app.import_config.load_form_json import load_form_jsons, load_json_from_file


# add files in /test_data t orun the below test against each file
@pytest.mark.parametrize(
    "filename,form_section_count",
    [
        ("optional-all-components.json", 4),
        ("required-all-components.json", 1),
    ],
)
def test_generate_config_for_round_valid_input(seed_dynamic_data, _db, filename, form_section_count):
    form_configs = []
    script_dir = os.path.dirname(__file__)
    test_data_dir = os.path.join(script_dir, "test_data")
    file_path = os.path.join(test_data_dir, filename)
    with open(file_path, "r") as json_file:
        form = json.load(json_file)
        form["filename"] = filename
        form_configs.append(form)
    load_form_jsons(form_configs)

    expected_form_count = 1
    expected_page_count_for_form = 8
    expected_component_count_for_form = 27
    # check form config is in the database
    forms = _db.session.query(Form).filter(Form.runner_publish_name == filename.split(".")[0])
    assert forms.count() == expected_form_count
    form = forms.first()
    pages = _db.session.query(Page).filter(Page.form_id == form.form_id)
    assert pages.count() == expected_page_count_for_form
    total_components_count = sum(
        _db.session.query(Component).filter(Component.page_id == page.page_id).count() for page in pages
    )
    assert total_components_count == expected_component_count_for_form
    form_sections = _db.session.query(FormSection)
    assert form_sections.count() == form_section_count


# TODO see why this fails
@pytest.mark.skip
def test_generate_config_for_round_valid_input_file(seed_dynamic_data, _db):
    filename = "test-import-form.json"
    template_name = "test-template"
    file_path = Path("tests") / "test_data" / filename
    with open(file_path, "r") as json_file:
        form = json.load(json_file)

    load_json_from_file(form, template_name, filename)

    expected_form_count = 1
    expected_page_count_for_form = 19
    expected_component_count_for_form = 25
    # check form config is in the database
    forms = _db.session.query(Form).filter(Form.template_name == template_name)
    assert forms.count() == expected_form_count
    form = forms.first()
    pages = _db.session.query(Page).filter(Page.form_id == form.form_id)
    assert pages.count() == expected_page_count_for_form
    total_components_count = sum(
        _db.session.query(Component).filter(Component.page_id == page.page_id).count() for page in pages
    )
    assert total_components_count == expected_component_count_for_form


def test_import_multi_input_field(seed_dynamic_data, _db):
    with open(Path("tests") / "test_data" / "multi_input.json", "r") as json_file:
        form = json.load(json_file)

    load_json_from_file(form, template_name="test_input_multi_input", filename="multi_input.json")
    forms = _db.session.query(Form).filter(Form.runner_publish_name == "multi_input")
    assert forms.count() == 1
    pages = _db.session.query(Page).filter(Page.form_id == forms.first().form_id)
    assert pages.count() == 3
    page_with_multi_input = next(p for p in pages if p.display_path == "capital-costs-for-your-project")
    assert page_with_multi_input
    assert page_with_multi_input.options
    multi_input_component = next(c for c in page_with_multi_input.components if c.title == "Capital costs")
    assert multi_input_component
    assert multi_input_component.type == ComponentType.MULTI_INPUT_FIELD
    assert len(multi_input_component.children) == 4


def test_creates_unique_lists_per_form_with_shared_list_name(app: Flask, clean_db: SQLAlchemy):
    with app.app_context():
        shared_list_name = "shared_list"
        form_config_1 = {
            "name": "Form 1",
            "startPage": "/start",
            "sections": [{"name": "section1", "title": "Section 1"}],
            "lists": [{"name": shared_list_name, "items": ["item1"]}],
            "pages": [{"path": "/start", "title": "Start Page", "components": [{"list": shared_list_name}]}],
            "conditions": [],
        }
        form_config_2 = {
            "name": "Form 2",
            "startPage": "/start",
            "sections": [{"name": "section1", "title": "Section 1"}],
            "lists": [{"name": shared_list_name, "items": ["item1"]}],
            "pages": [{"path": "/start", "title": "Start Page", "components": [{"list": shared_list_name}]}],
            "conditions": [],
        }
        with (
            patch("app.import_config.load_form_json.create_form_sections_db") as mock_create_sections,
            patch("app.import_config.load_form_json.insert_page_as_template") as mock_insert_page,
            patch("app.import_config.load_form_json.insert_component_as_template") as mock_insert_component,
        ):

            # Create a mock form section with the required name property
            mock_form_section = MagicMock()
            mock_form_section.name = "FabDefault"
            mock_form_section.form_section_id = uuid4()

            mock_create_sections.return_value = [mock_form_section]
            mock_insert_page.return_value = MagicMock(page_id=1)
            mock_insert_component.return_value = MagicMock(component_id=1)

            # Load both forms
            load_json_from_file(form_config_1, "form1", "form1.json")
            load_json_from_file(form_config_2, "form2", "form2.json")

            # Query lists and verify
            lists = clean_db.session.query(Lizt).all()
            assert len(lists) == 2
            assert lists[0].name == "shared_list"
            assert lists[1].name == "shared_list"
            assert lists[0].list_id != lists[1].list_id
