from dataclasses import asdict
from unittest import mock
from uuid import uuid4

import pytest

from app.db.models.application_config import Component
from app.import_config.load_form_json import _build_condition, add_conditions_to_components
from app.shared.data_classes import Condition, ConditionValue, SubCondition
from tests.unit_test_data import (
    test_condition_org_type_a,
    test_condition_org_type_c,
    test_form_json_condition_org_type_a,
    test_form_json_condition_org_type_c,
)


@pytest.mark.parametrize(
    "input_condition,exp_result",
    [
        (
            test_form_json_condition_org_type_a,
            test_condition_org_type_a,
        ),
        (
            test_form_json_condition_org_type_c,
            test_condition_org_type_c,
        ),
    ],
)
def test_build_conditions(input_condition, exp_result):
    result = _build_condition(
        condition_data=input_condition, source_page_path=None, destination_page_path=exp_result.destination_page_path
    )
    assert result == exp_result


@pytest.mark.parametrize(
    "input_page, input_conditions, exp_condition_count",
    [
        ({"path": "/here", "next": [{"path": "default-next"}]}, [], 0),
        (
            {"path": "/here", "next": [{"path": "next-a", "condition": "condition-a"}]},
            [
                asdict(
                    Condition(
                        name="condition-a",
                        display_name="condition a",
                        destination_page_path="page-b",
                        value=ConditionValue(
                            name="condition a",
                            conditions=[SubCondition(field={"name": "c1"}, operator="is", value={}, coordinator=None)],
                        ),
                    )
                )
            ],
            1,
        ),
        (
            {"path": "/here", "next": [{"path": "next-a", "condition": "condition-a"}]},
            [
                asdict(
                    Condition(
                        name="condition-a",
                        display_name="condition a",
                        destination_page_path="page-b",
                        value=ConditionValue(
                            name="condition a",
                            conditions=[
                                SubCondition(field={"name": "c1"}, operator="is", value={}, coordinator=None),
                                SubCondition(field={"name": "c1"}, operator="is", value={}, coordinator="or"),
                            ],
                        ),
                    )
                )
            ],
            1,
        ),
    ],
)
def test_add_conditions_to_components(mocker, input_page, input_conditions, exp_condition_count):
    mock_component = Component()
    mocker.patch("app.import_config.load_form_json._get_component_by_runner_name", return_value=mock_component)
    mocker.patch("app.import_config.load_form_json.get_all_pages_in_parent_form", return_value=[uuid4()])

    # Set up other necessary mocks and test data
    with mock.patch(
        "app.import_config.load_form_json._build_condition",
        return_value=Condition(name=None, display_name=None, destination_page_path=None, value=None),
    ) as mock_build_condition:
        add_conditions_to_components(None, input_page, input_conditions, page_id=None)
        if exp_condition_count > 0:
            assert mock_component.conditions
            assert len(mock_component.conditions) == exp_condition_count
        assert mock_build_condition.call_count == len(input_conditions)


@pytest.mark.parametrize(
    "input_page, input_conditions, exp_condition_count",
    [
        (
            [
                {"path": "/path-1", "next": [{"path": "next-a", "condition": "condition-a"}]},
                {"path": "/path-2", "next": [{"path": "next-a", "condition": "condition-a"}]},
                {"path": "/path-3", "next": [{"path": "next-a", "condition": "condition-a"}]},
            ],
            [
                asdict(
                    Condition(
                        name="condition-a",
                        display_name="condition a",
                        destination_page_path="page-b",
                        value=ConditionValue(
                            name="condition a",
                            conditions=[
                                SubCondition(field={"name": "c1"}, operator="is", value={}, coordinator=None),
                                SubCondition(field={"name": "c1"}, operator="is", value={}, coordinator="or"),
                            ],
                        ),
                    )
                )
            ],
            1,
        ),
    ],
)
def test_same_condition_used_in_different_pages(mocker, input_page, input_conditions, exp_condition_count):
    mock_component = Component()
    mocker.patch("app.import_config.load_form_json._get_component_by_runner_name", return_value=mock_component)
    mocker.patch("app.import_config.load_form_json.get_all_pages_in_parent_form", return_value=[uuid4()])

    # Set up other necessary mocks and test data
    with mock.patch(
        "app.import_config.load_form_json._build_condition",
        return_value=Condition(name=None, display_name=None, destination_page_path=None, value=None),
    ):
        for page in input_page:
            add_conditions_to_components(None, page, input_conditions, page_id=None)
        assert mock_component.conditions
        assert len(mock_component.conditions) == exp_condition_count
