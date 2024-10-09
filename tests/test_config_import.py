import json
import os

import pytest

from app.db.models import Component
from app.db.models import Form
from app.db.models import Page
from app.import_config.load_form_json import load_form_jsons
from app.import_config.load_form_json import load_json_from_file


# add files in /test_data t orun the below test against each file
@pytest.mark.parametrize(
    "filename",
    [
        "optional-all-components.json",
        "required-all-components.json",
    ],
)
def test_generate_config_for_round_valid_input(seed_dynamic_data, _db, filename):
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
    forms = _db.session.query(Form).filter(Form.template_name == filename.split(".")[0])
    assert forms.count() == expected_form_count
    form = forms.first()
    pages = _db.session.query(Page).filter(Page.form_id == form.form_id)
    assert pages.count() == expected_page_count_for_form
    total_components_count = sum(
        _db.session.query(Component).filter(Component.page_id == page.page_id).count() for page in pages
    )
    assert total_components_count == expected_component_count_for_form


# TODO see why this fails
@pytest.mark.skip
def test_generate_config_for_round_valid_input_file(seed_dynamic_data, _db):
    filename = "test-import-form.json"
    template_name = "test-template"
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, filename)
    with open(file_path, "r") as json_file:
        form = json.load(json_file)
        form["filename"] = filename

    load_json_from_file(form, template_name)

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
