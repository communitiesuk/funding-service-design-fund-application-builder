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
        "rounds": [Round(round_id=round_id, fund_id=fund_id, short_name="UTRWC", **BASIC_ROUND_INFO)],
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
    assert len(org_name_page["next"]) == 2
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
