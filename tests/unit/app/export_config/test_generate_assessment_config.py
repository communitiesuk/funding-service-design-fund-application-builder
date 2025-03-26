from app.db.models import Fund
from app.export_config.generate_assessment_config import build_assessment_config
from tests.helpers import get_fund_by_id
from tests.unit_test_data import cri1, crit_1_id, mock_form_1


def test_build_basic_structure(mocker):
    mocker.patch("app.export_config.generate_assessment_config.get_form_for_component", return_value=mock_form_1)

    results = build_assessment_config([cri1])
    assert "unscored_sections" in results
    unscored = next(section for section in results["unscored_sections"] if section["id"] == crit_1_id)
    assert unscored["name"] == "Unscored"


def test_with_field_info(mocker):
    mocker.patch("app.export_config.generate_assessment_config.get_form_for_component", return_value=mock_form_1)
    results = build_assessment_config([cri1])
    assert len(results["unscored_sections"]) == 1
    unscored_subcriteria = next(section for section in results["unscored_sections"] if section["id"] == crit_1_id)[
        "subcriteria"
    ]
    assert unscored_subcriteria
    assert unscored_subcriteria[0]["name"] == "Organisation Information"

    unscored_themes = unscored_subcriteria[0]["themes"]
    assert len(unscored_themes) == 1

    general_info = unscored_themes[0]
    assert general_info["name"] == "General Information"
    assert len(general_info["answers"]) == 2


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
