from app.config_generator.scripts.generate_assessment_config import (
    build_assessment_config,
)
from tests.unit_test_data import cri1
from tests.unit_test_data import crit_1_id
from tests.unit_test_data import mock_form_1


def test_build_basic_structure(mocker):
    mocker.patch(
        "app.config_generator.scripts.generate_assessment_config.get_form_for_component", return_value=mock_form_1
    )

    results = build_assessment_config([cri1])
    assert "unscored_sections" in results
    unscored = next(section for section in results["unscored_sections"] if section["id"] == crit_1_id)
    assert unscored["name"] == "Unscored"


def test_with_field_info(mocker):

    mocker.patch(
        "app.config_generator.scripts.generate_assessment_config.get_form_for_component", return_value=mock_form_1
    )
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
