from dataclasses import asdict
from unittest import mock
from uuid import uuid4

import pytest

from app.db.models.application_config import Component
from app.db.models.application_config import Lizt
from app.import_config.load_form_json import _build_condition
from app.import_config.load_form_json import _find_list_and_create_if_not_existing
from app.import_config.load_form_json import add_conditions_to_components
from app.shared.data_classes import Condition
from app.shared.data_classes import ConditionValue
from app.shared.data_classes import SubCondition
from tests.unit_test_data import test_condition_org_type_a
from tests.unit_test_data import test_condition_org_type_c
from tests.unit_test_data import test_form_json_condition_org_type_a
from tests.unit_test_data import test_form_json_condition_org_type_c


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
    result = _build_condition(condition_data=input_condition, source_page_path=None, destination_page_path=exp_result.destination_page_path)
    assert result == exp_result


@pytest.mark.parametrize(
    "input_page, input_conditions, exp_condition_count",
    [
        ({"path":"/here",
          "next": [{"path": "default-next"}]}, [], 0),
        (
            {"path":"/here","next": [{"path": "next-a", "condition": "condition-a"}]},
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
            {"path":"/here","next": [{"path": "next-a", "condition": "condition-a"}]},
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
    db = mocker.Mock()
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
    "input_list_name,input_all_lists, existing_list",
    [
        ("existing-list", [{"name": "existing-list"}], Lizt(list_id=uuid4())),
    ],
)
def test_find_list_and_create_existing(mocker, input_list_name, input_all_lists, existing_list):
    with (
        mock.patch(
            "app.import_config.load_form_json.get_list_by_name", return_value=existing_list
        ) as get_list_by_name_mock,
        mock.patch(
            "app.import_config.load_form_json.insert_list", return_value=Lizt(list_id="new-list-id")
        ) as insert_list_mock,
    ):
        result = _find_list_and_create_if_not_existing(list_name=input_list_name, all_lists_in_form=input_all_lists)
        assert result == existing_list.list_id
        assert get_list_by_name_mock.called_once_with(list_name=input_list_name)
        insert_list_mock.assert_not_called()


@pytest.mark.parametrize("input_list_name,input_all_lists, existing_list", [("new-list", [{"name": "new-list"}], None)])
def test_find_list_and_create_not_existing(mocker, input_list_name, input_all_lists, existing_list):
    with (
        mock.patch(
            "app.import_config.load_form_json.get_list_by_name", return_value=existing_list
        ) as get_list_by_name_mock,
        mock.patch(
            "app.import_config.load_form_json.insert_list", return_value=Lizt(list_id="new-list-id")
        ) as insert_list_mock,
    ):
        result = _find_list_and_create_if_not_existing(list_name=input_list_name, all_lists_in_form=input_all_lists)
        assert result == "new-list-id"
        assert get_list_by_name_mock.called_once_with(list_name=input_list_name)
        insert_list_mock.called_once()
