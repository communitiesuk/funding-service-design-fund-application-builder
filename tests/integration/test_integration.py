import json
from pathlib import Path

import pytest

from app.db.models import Form, Section
from app.export_config.generate_fund_round_form_jsons import (
    generate_form_jsons_for_round,
)
from app.import_config.load_form_json import load_form_jsons


@pytest.mark.parametrize(
    "input_filename, output_filename",
    [
        ("test-section.json", "test-section.json"),
    ],
)
def test_generate_config_to_verify_form_sections(
    seed_dynamic_data,
    _db,
    monkeypatch,
    input_filename,
    output_filename,
    temp_output_dir,
):
    form_configs = []
    file_path = Path("tests") / "test_data" / input_filename
    with open(file_path, "r") as json_file:
        input_form = json.load(json_file)
        form_config = {
            "filename": input_filename,
            "form_json": input_form,
        }
        form_configs.append(form_config)
    load_form_jsons(form_configs)

    round_id = seed_dynamic_data["rounds"][0].round_id
    round_short_name = seed_dynamic_data["rounds"][0].short_name
    mock_round_base_paths = {round_short_name: 99}
    # find a random section belonging to the round id and assign each form to that section
    forms = _db.session.query(Form).filter(Form.runner_publish_name == input_filename.split(".")[0])
    section = _db.session.query(Section).filter(Section.round_id == round_id).first()
    for form in forms:
        form.section_id = section.section_id
    _db.session.commit()

    # Use monkeypatch to temporarily replace ROUND_BASE_PATHS
    import app.export_config.generate_fund_round_config as generate_fund_round_config

    monkeypatch.setattr(generate_fund_round_config, "ROUND_BASE_PATHS", mock_round_base_paths)
    result = generate_form_jsons_for_round(round_id)
    # Simply writes the files to the output directory so no result is given directly
    assert result is None

    # Check if the directory is created
    generated_json_form = temp_output_dir / round_short_name / "form_runner" / output_filename
    assert generated_json_form

    # compare the import file with the generated file
    with open(generated_json_form, "r") as file:
        output_form = json.load(file)

    assert len(output_form["sections"]) == len(form_configs[0]["form_json"]["sections"])


@pytest.mark.parametrize(
    "input_filename, output_filename,expected_page_count_for_form,expected_component_count_for_form, "
    "expected_form_section_count",
    [
        ("projects.json", "projects.json", 4, 5, 1),
        ("asset-information.json", "asset-information.json", 23, 29, 1),
        ("org-info.json", "org-info.json", 18, 43, 1),
        ("optional-all-components.json", "optional-all-components.json", 8, 27, 3),
        ("required-all-components.json", "required-all-components.json", 8, 27, 0),
        ("favourite-colours.json", "favourite-colours.json", 4, 1, 0),
        ("funding-required-cof-25.json", "funding-required-cof-25.json", 12, 21, 1),
        (
            "organisation-and-local-authority.json",
            "organisation-and-local-authority.json",
            16,
            24,
            1,
        ),  # noqa: E501
        ("test-section.json", "test-section.json", 3, 1, 2),
    ],
)
def test_generate_config_for_round_valid_input(
    seed_dynamic_data,
    _db,
    monkeypatch,
    input_filename,
    output_filename,
    expected_page_count_for_form,
    expected_component_count_for_form,
    expected_form_section_count,
    temp_output_dir,
):
    form_configs = []
    file_path = Path("tests") / "test_data" / input_filename
    with open(file_path, "r") as json_file:
        input_form = json.load(json_file)
        form_config = {
            "filename": input_filename,
            "form_json": input_form,
        }
        form_configs.append(form_config)
    load_form_jsons(form_configs)

    expected_form_count = 1
    # check form config is in the database
    forms = _db.session.query(Form).filter(Form.runner_publish_name == input_filename.split(".")[0])
    assert forms.count() == expected_form_count
    form = forms.first()

    assert len(form.form_json["pages"]) == expected_page_count_for_form
    assert len(form.form_json["sections"]) == expected_form_section_count
    num_components = 0
    for page in form.form_json["pages"]:
        num_components += len(page["components"])
    assert num_components == expected_component_count_for_form

    # PART 2 GENERATE FORM JSON'S
    # associate forms with a round
    round_id = seed_dynamic_data["rounds"][0].round_id
    round_short_name = seed_dynamic_data["rounds"][0].short_name
    mock_round_base_paths = {round_short_name: 99}
    # find a random section belonging to the round id and assign each form to that section
    section = _db.session.query(Section).filter(Section.round_id == round_id).first()
    for form in forms:
        form.section_id = section.section_id
    _db.session.commit()

    # Use monkeypatch to temporarily replace ROUND_BASE_PATHS
    import app.export_config.generate_fund_round_config as generate_fund_round_config

    monkeypatch.setattr(generate_fund_round_config, "ROUND_BASE_PATHS", mock_round_base_paths)
    result = generate_form_jsons_for_round(round_id)
    # Simply writes the files to the output directory so no result is given directly
    assert result is None

    # Check if the directory is created
    generated_json_form = temp_output_dir / round_short_name / "form_runner" / output_filename
    assert generated_json_form

    # compare the import file with the generated file
    with open(generated_json_form, "r") as file:
        output_form = json.load(file)

    # Compare the contents of the files

    # ensure the keys of the output form are in the input form keys
    assert set(output_form.keys()) - {"name"} <= set(input_form.keys()), (
        "Output form keys are not a subset of input form keys, ignoring 'name'"
    )

    # check conditions length is equal
    input_condition_count = len(input_form.get("conditions", []))
    output_condition_count = len(output_form.get("conditions", []))
    assert output_condition_count <= input_condition_count  # sometime we remove specified but unused conditions

    _assert_sorted_equal(output_form, input_form, "lists")
    _assert_sorted_equal(output_form, input_form, "conditions")

    # check that content of each page (including page[components] and page[next] within form[pages] is the same
    for input_page in input_form["pages"]:
        # find page in output pages
        output_page = next((p for p in output_form["pages"] if p["path"] == input_page["path"]), None)
        assert input_page["path"] == output_page["path"]
        assert input_page["title"] == output_page["title"]
        for next_dict in input_page["next"]:
            # find next in output page
            output_next = next((n for n in output_page["next"] if n["path"] == next_dict["path"]), None)
            assert next_dict["path"] == output_next["path"]
            assert next_dict.get("condition", None) == output_next.get("condition", None)

        # compare components
        for input_component in input_page["components"]:
            # find component in output page
            output_component = None
            for c in output_page.get("components", []):
                # Get name or content for both components safely
                output_name_or_content = c.get("name") or c.get("content")
                input_name_or_content = input_component.get("name") or input_component.get("content")
                print(f"Checking output: {output_name_or_content} vs input: {input_name_or_content}")
                if output_name_or_content == input_name_or_content:
                    output_component = c
                    break

            for key in input_component:
                assert input_component[key] == output_component[key]


def _assert_sorted_equal(output, input_data, key):
    if key in input_data and input_data[key]:
        sorted_output = sorted(output[key], key=lambda x: x["name"])
        sorted_input = sorted(input_data[key], key=lambda x: x["name"])
        assert sorted_output == sorted_input
