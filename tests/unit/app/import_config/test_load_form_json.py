import json
from pathlib import Path

import pytest

from app.db.models.application_config import Component, Form, Page
from app.import_config.load_form_json import load_form_jsons, load_json_from_file


# add files in /test_data t orun the below test against each file
@pytest.mark.parametrize(
    "filename,form_section_count",
    [
        ("optional-all-components.json", 3),
        ("required-all-components.json", 0),
    ],
)
def test_generate_config_for_round_valid_input(seed_dynamic_data, _db, filename, form_section_count):
    form_configs = []
    file_path = Path("tests") / "test_data" / filename
    with open(file_path, "r") as json_file:
        form = json.load(json_file)
        form_config = {
            "filename": filename,
            "form_json": form,
        }
        form_configs.append(form_config)
    load_form_jsons(form_configs)

    expected_form_count = 1
    expected_page_count_for_form = 8
    expected_component_count_for_form = 27
    # check form config is in the database
    forms = _db.session.query(Form).filter(Form.runner_publish_name == filename.split(".")[0])
    assert forms.count() == expected_form_count
    form: Form = forms.first()
    assert len(form.form_json["pages"]) == expected_page_count_for_form
    num_components = 0
    for page in form.form_json["pages"]:
        num_components += len(page.get("components", []))
    assert num_components == expected_component_count_for_form
    assert len(form.form_json["sections"]) == form_section_count


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

    form_record: Form = forms.first()
    form_json = form_record.form_json

    # Access pages directly from form_json
    pages = form_json["pages"]
    assert len(pages) == 3

    # Find the page with multi input by path
    page_with_multi_input = next((p for p in pages if p.get("path") == "/capital-costs-for-your-project"), None)
    assert page_with_multi_input is not None
    assert page_with_multi_input.get("options") is not None

    # Access components directly from the page dict
    components = page_with_multi_input.get("components", [])
    multi_input_component = next((c for c in components if c.get("title") == "Capital costs"), None)
    assert multi_input_component is not None
    assert multi_input_component.get("type") == "MultiInputField"  # Assuming this is the string representation

    # Check children components directly from the component dict
    children_components = multi_input_component.get("children", [])
    assert len(children_components) == 4
