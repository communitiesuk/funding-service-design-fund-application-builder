import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

import pytest

from app.db.models import Component
from app.db.models import ComponentType
from app.db.models import Form
from app.db.models import Fund
from app.db.models import Lizt
from app.db.models import Page
from app.db.models import Round
from app.db.models import Section
from app.db.queries.application import get_component_by_id
from app.db.queries.fund import get_fund_by_id
from app.export_config.generate_assessment_config import build_assessment_config
from app.export_config.generate_form import build_form_json
from app.export_config.generate_fund_round_form_jsons import (
    generate_form_jsons_for_round,
)
from app.import_config.load_form_json import load_form_jsons
from app.shared.data_classes import Condition
from app.shared.data_classes import ConditionValue
from tasks.test_data import BASIC_FUND_INFO
from tasks.test_data import BASIC_ROUND_INFO


def test_build_form_json_no_conditions(seed_dynamic_data):

    f: Fund = get_fund_by_id(seed_dynamic_data["funds"][0].fund_id)
    form: Form = f.rounds[0].sections[0].forms[0]

    result = build_form_json(form=form)
    assert result
    assert len(result["pages"]) == 3
    exp_start_path = "/intro-about-your-organisation"
    exp_second_path = "/organisation-name"
    assert result["startPage"] == exp_start_path
    intro_page = next((p for p in result["pages"] if p["path"] == exp_start_path), None)
    assert intro_page
    assert intro_page["next"][0]["path"] == exp_second_path

    org_name_page = next((p for p in result["pages"] if p["path"] == exp_second_path), None)
    assert org_name_page
    assert len(org_name_page["next"]) == 1

    # alt_names_page = next((p for p in result["pages"] if p["path"] == "/organisation-alternative-names"), None)
    # assert alt_names_page
    # assert alt_names_page["next"][0]["path"] == "/organisation-address"

    # address_page = next((p for p in result["pages"] if p["path"] == "/organisation-address"), None)
    # assert address_page
    # assert address_page["next"][0]["path"] == "/organisation-classification"

    # assert (
    #     next((p for p in result["pages"] if p["path"] == "/organisation-classification"), None)["next"][0]["path"]
    #     == "/summary"
    # )
    assert len(org_name_page["next"]) == 1
    assert org_name_page["next"][0]["path"] == "/summary"
    assert len(org_name_page["components"]) == 2

    summary = next((p for p in result["pages"] if p["path"] == "/summary"), None)
    assert summary


fund_id = uuid4()
round_id = uuid4()
section_id = uuid4()
form_id = uuid4()
page_1_id = uuid4()
page_2_id = uuid4()


@pytest.mark.seed_config(
    {
        "funds": [Fund(fund_id=fund_id, short_name="UTFWC", **BASIC_FUND_INFO)],
        "rounds": [
            Round(
                round_id=round_id, title_json={"en": "UT RWC"}, fund_id=fund_id, short_name="UTRWC", **BASIC_ROUND_INFO
            )
        ],
        "sections": [
            Section(
                section_id=section_id, index=1, round_id=round_id, name_in_apply_json={"en": "Organisation Information"}
            )
        ],
        "forms": [
            Form(
                form_id=form_id,
                section_id=section_id,
                name_in_apply_json={"en": "About your organisation"},
                section_index=1,
                runner_publish_name="about-your-org",
            )
        ],
        "pages": [
            Page(
                page_id=page_1_id,
                form_id=form_id,
                display_path="organisation-name",
                name_in_apply_json={"en": "Organisation Name"},
                form_index=1,
            ),
            Page(
                page_id=page_2_id,
                form_id=form_id,
                display_path="organisation-alternative-names",
                name_in_apply_json={"en": "Alternative names of your organisation"},
                form_index=2,
                is_template=True,
            ),
        ],
        "default_next_pages": [
            {"page_id": page_1_id, "default_next_page_id": page_2_id},
        ],
        "components": [
            Component(
                component_id=uuid4(),
                page_id=page_1_id,
                title="What is your organisation's name?",
                hint_text="This must match the regsitered legal organisation name",
                type=ComponentType.TEXT_FIELD,
                page_index=1,
                theme_id=None,
                options={"hideTitle": False, "classes": ""},
                runner_component_name="organisation_name",
            ),
            Component(
                component_id=uuid4(),
                page_id=page_1_id,
                title="Does your organisation use any other names?",
                type=ComponentType.YES_NO_FIELD,
                page_index=2,
                theme_id=None,
                options={"hideTitle": False, "classes": ""},
                runner_component_name="does_your_organisation_use_other_names",
                is_template=True,
                conditions=[
                    asdict(
                        Condition(
                            name="organisation_other_names_no",
                            display_name="org other names no",
                            destination_page_path="/summary",
                            value=ConditionValue(
                                name="org other names no",
                                conditions=[
                                    {
                                        "field": {
                                            "name": "org_other_names",
                                            "type": "YesNoField",
                                            "display": "org other names",
                                        },
                                        "operator": "is",
                                        "value": {"type": "Value", "value": "false", "display": "false"},
                                        "coordinator": None,
                                    },
                                ],
                            ),
                        ),
                    ),
                    asdict(
                        Condition(
                            name="organisation_other_names_yes",
                            display_name="org other names yes",
                            destination_page_path="/organisation-alternative-names",
                            value=ConditionValue(
                                name="org other names yes",
                                conditions=[
                                    {
                                        "field": {
                                            "name": "org_other_names",
                                            "type": "YesNoField",
                                            "display": "org other names",
                                        },
                                        "operator": "is",
                                        "value": {"type": "Value", "value": "true", "display": "false"},
                                        "coordinator": None,
                                    },
                                ],
                            ),
                        ),
                    ),
                ],
            ),
            Component(
                component_id=uuid4(),
                page_id=page_2_id,
                title="Alternative Name 1",
                type=ComponentType.TEXT_FIELD,
                page_index=1,
                theme_id=None,
                options={"hideTitle": False, "classes": ""},
                runner_component_name="alt_name_1",
                is_template=True,
            ),
        ],
    }
)
def test_build_form_json_with_conditions(seed_dynamic_data):

    f: Fund = get_fund_by_id(seed_dynamic_data["funds"][0].fund_id)
    form: Form = f.rounds[0].sections[0].forms[0]

    result = build_form_json(form=form)
    assert result
    assert len(result["pages"]) == 4
    exp_start_path = "/intro-about-your-organisation"
    exp_second_path = "/organisation-name"
    assert result["startPage"] == exp_start_path
    intro_page = next((p for p in result["pages"] if p["path"] == exp_start_path), None)
    assert intro_page
    assert intro_page["next"][0]["path"] == exp_second_path

    org_name_page = next((p for p in result["pages"] if p["path"] == exp_second_path), None)
    assert org_name_page
    assert len(org_name_page["next"]) == 3
    assert len(org_name_page["components"]) == 2

    alt_names_page = next((p for p in result["pages"] if p["path"] == "/organisation-alternative-names"), None)
    assert alt_names_page
    assert alt_names_page["next"][0]["path"] == "/summary"
    assert len(alt_names_page["components"]) == 1

    summary = next((p for p in result["pages"] if p["path"] == "/summary"), None)
    assert summary


# TODO this fails with components from a template (branching logic)
def test_build_assessment_config_no_branching(seed_dynamic_data):

    f: Fund = get_fund_by_id(seed_dynamic_data["funds"][0].fund_id)
    criteria = f.rounds[0].criteria[0]
    result = build_assessment_config(criteria_list=[criteria])
    assert result
    first_unscored = result["unscored_sections"][0]
    assert first_unscored
    assert first_unscored["name"] == "Unscored"
    assert len(first_unscored["subcriteria"]) == 1
    assert len(first_unscored["subcriteria"][0]["themes"]) == 1
    assert len(first_unscored["subcriteria"][0]["themes"][0]["answers"]) == 2


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


output_base_path = Path("app") / "export_config" / "output"


# add files in /test_data t orun the below test against each file
@pytest.mark.parametrize(
    "filename,expected_page_count_for_form,expected_component_count_for_form",
    [
        ("org-info.json", 18, 43),
        ("optional-all-components.json", 8, 27),
        ("required-all-components.json", 8, 27),
    ],
)
def test_generate_config_for_round_valid_input(
    seed_dynamic_data, _db, monkeypatch, filename, expected_page_count_for_form, expected_component_count_for_form
):
    form_configs = []
    script_dir = os.path.dirname(__file__)
    test_data_dir = os.path.join(script_dir, "test_data")
    file_path = os.path.join(test_data_dir, filename)
    with open(file_path, "r") as json_file:
        input_form = json.load(json_file)
        input_form["filename"] = filename
        form_configs.append(input_form)
    load_form_jsons(form_configs)

    expected_form_count = 1
    # check form config is in the database
    forms = _db.session.query(Form).filter(Form.template_name == filename)
    assert forms.count() == expected_form_count
    form = forms.first()
    pages = _db.session.query(Page).filter(Page.form_id == form.form_id)
    assert pages.count() == expected_page_count_for_form
    total_components_count = sum(
        _db.session.query(Component).filter(Component.page_id == page.page_id).count() for page in pages
    )
    assert total_components_count == expected_component_count_for_form

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

    try:
        # Check if the directory is created
        generated_json_form = output_base_path / round_short_name / "form_runner" / filename
        assert generated_json_form

        # compare the import file with the generated file
        with open(generated_json_form, "r") as file:
            output_form = json.load(file)

        # Compare the contents of the files

        # ensure the keys of the output form are in the input form keys
        assert set(output_form.keys()) - {"name"} <= set(
            input_form.keys()
        ), "Output form keys are not a subset of input form keys, ignoring 'name'"

        # check conditions length is equal
        input_condition_count = len(input_form.get("conditions", []))
        output_condition_count = len(output_form.get("conditions", []))
        assert output_condition_count <= input_condition_count  # sometime we remove specified but unused conditions

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
    finally:
        # Cleanup step to remove the directory
        directory_path = output_base_path / round_short_name
        if directory_path.exists():
            shutil.rmtree(directory_path)
