from dataclasses import asdict
from unittest import mock

import pytest

from app.db.models.application_config import Component
from app.import_config.load_form_json import _build_condition
from app.import_config.load_form_json import add_conditions_to_components
from app.shared.data_classes import Condition
from app.shared.data_classes import ConditionValue
from app.shared.data_classes import SubCondition


@pytest.mark.parametrize(
    "input_condition,exp_result",
    [
        (
            {
                "displayName": "org type a",
                "name": "org_type_a",
                "value": {
                    "name": "org type a",
                    "conditions": [
                        {
                            "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                            "operator": "is",
                            "value": {"type": "Value", "value": "A", "display": "A"},
                        }
                    ],
                },
            },
            Condition(
                name="org_type_a",
                display_name="org type a",
                destination_page_path="/page-1",
                value=ConditionValue(
                    name="org type a",
                    conditions=[
                        {
                            "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                            "operator": "is",
                            "value": {"type": "Value", "value": "A", "display": "A"},
                        }
                    ],
                ),
            ),
        ),
        (
            {
                "displayName": "org type c",
                "name": "org_type_c",
                "value": {
                    "name": "org type c",
                    "conditions": [
                        {
                            "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                            "operator": "is",
                            "value": {"type": "Value", "value": "C1", "display": "C1"},
                        },
                        {
                            "coordinator": "or",
                            "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                            "operator": "is",
                            "value": {"type": "Value", "value": "C2", "display": "C2"},
                        },
                    ],
                },
            },
            Condition(
                name="org_type_c",
                display_name="org type c",
                destination_page_path="/page-1",
                value=ConditionValue(
                    name="org type c",
                    conditions=[
                        {
                            "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                            "operator": "is",
                            "value": {"type": "Value", "value": "C1", "display": "C1"},
                        },
                        {
                            "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                            "operator": "is",
                            "value": {"type": "Value", "value": "C2", "display": "C2"},
                            "coordinator": "or",
                        },
                    ],
                ),
            ),
        ),
    ],
)
def test_build_conditions(input_condition, exp_result):
    result = _build_condition(condition_data=input_condition, destination_page_path="/page-1")
    assert result == exp_result


@pytest.mark.parametrize(
    "input_page, input_conditions, exp_condition_count",
    [
        ({"next": [{"path": "default-next"}]}, [], 0),
        (
            {"next": [{"path": "next-a", "condition": "condition-a"}]},
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
            {"next": [{"path": "next-a", "condition": "condition-a"}]},
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
    with mock.patch(
        "app.import_config.load_form_json._build_condition",
        return_value=Condition(name=None, display_name=None, destination_page_path=None, value=None),
    ) as mock_build_condition:
        add_conditions_to_components(None, input_page, input_conditions)
        if exp_condition_count > 0:
            assert mock_component.conditions
            assert len(mock_component.conditions) == exp_condition_count
        assert mock_build_condition.call_count == len(input_conditions)
