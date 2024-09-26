from unittest import mock
from uuid import uuid4

import pytest

from app.db.models import Component
from app.db.models import ComponentType
from app.db.models import Lizt
from app.db.models import Page
from app.export_config.generate_form import build_component
from app.export_config.generate_form import build_conditions
from app.export_config.generate_form import build_form_json
from app.export_config.generate_form import build_lists
from app.export_config.generate_form import build_navigation
from app.export_config.generate_form import build_page
from app.export_config.generate_form import human_to_kebab_case
from tests.unit_test_data import mock_c_1
from tests.unit_test_data import mock_c_2
from tests.unit_test_data import mock_form_1


@pytest.mark.parametrize(
    "input, exp_output", [("", None), ("hello world", "hello-world"), ("Hi There Everyone", "hi-there-everyone")]
)
def test_human_to_kebab(input, exp_output):
    result = human_to_kebab_case(input)
    assert result == exp_output


@pytest.mark.parametrize(
    "pages, exp_result",
    [
        (
            [{"components": [{"list": "greetings_list", "metadata": {"fund_builder_list_id": 123}}]}],
            [
                {
                    "name": "greetings_list",
                    "type": "string",
                    "items": [{"text": "Hello", "value": "h"}, {"text": "Goodbye", "value": "g"}],
                }
            ],
        ),
        (
            [
                {"components": [{"list": "greetings_list", "metadata": {"fund_builder_list_id": 123}}]},
                {"components": [{"metadata": {}}]},
            ],
            [
                {
                    "name": "greetings_list",
                    "type": "string",
                    "items": [{"text": "Hello", "value": "h"}, {"text": "Goodbye", "value": "g"}],
                }
            ],
        ),
        (
            [
                {"components": [{"list": "greetings_list", "metadata": {"fund_builder_list_id": 123}}]},
                {"components": [{"metadata": {}}]},
                {"components": [{"list": "greetings_list", "metadata": {"fund_builder_list_id": 123}}]},
            ],
            [
                {
                    "name": "greetings_list",
                    "type": "string",
                    "items": [{"text": "Hello", "value": "h"}, {"text": "Goodbye", "value": "g"}],
                },
            ],
        ),
    ],
)
def test_build_lists(mocker, pages, exp_result):
    mocker.patch(
        "app.export_config.generate_form.get_list_by_id",
        return_value=Lizt(
            name="greetings_list",
            type="string",
            items=[{"text": "Hello", "value": "h"}, {"text": "Goodbye", "value": "g"}],
        ),
    )
    results = build_lists(pages)
    assert len(results) == len(exp_result)
    assert results[0]["name"] == "greetings_list"


mock_lookups = {
    "organisation-name": "Organisation Name",
    "organisation-single-name": "Organisation Name",
}
mock_components = [
    {
        "id": "reuse-charitable-objects",
        "json_snippet": {
            "options": {"hideTitle": True, "maxWords": "500"},
            "type": "FreeTextField",
            "title": "What are your organisation’s charitable objects?",
            "hint": "You can find this in your organisation's governing document.",
        },
    },
    {
        "id": "reuse-organisation-name",
        "json_snippet": {
            "options": {"hideTitle": False, "classes": "govuk-!-width-full"},
            "type": "TextField",
            "title": "Organisation name",
            "hint": "This must match your registered legal organisation name",
            "schema": {},
        },
    },
    {
        "id": "reuse_organisation_other_names_yes_no",
        "json_snippet": {
            "options": {},
            "type": "YesNoField",
            "title": "Does your organisation use any other names?",
            "schema": {},
        },
        "conditions": [
            {
                "name": "organisation_other_names_no",
                "value": "false",
                "operator": "is",
                "destination_page": "CONTINUE",
            },
            {
                "name": "organisation_other_names_yes",
                "value": "true",
                "operator": "is",
                "destination_page": "alternative-organisation-name",
            },
        ],
    },
    {
        "id": "reuse-alt-org-name-1",
        "json_snippet": {
            "options": {"classes": "govuk-input"},
            "type": "TextField",
            "title": "Alternative name 1",
            "schema": {},
        },
    },
    {
        "id": "reuse-alt-org-name-2",
        "json_snippet": {
            "options": {"required": False, "classes": "govuk-input"},
            "type": "TextField",
            "title": "Alternative name 2",
            "schema": {},
        },
    },
    {
        "id": "reuse-alt-org-name-3",
        "json_snippet": {
            "options": {"required": False, "classes": "govuk-input"},
            "type": "TextField",
            "title": "Alternative name 3",
            "schema": {},
        },
    },
]
mock_pages = [
    {
        "id": "organisation-single-name",
        "builder_display_name": "Single Organisation Name",
        "form_display_name": "Organisation Name",
        "component_names": [
            "reuse-organisation-name",
        ],
        "show_in_builder": True,
    },
    {
        "id": "organisation-name",
        "builder_display_name": "Organisation Name, with Alternatives",
        "form_display_name": "Organisation Name",
        "component_names": [
            "reuse-organisation-name",
            "reuse_organisation_other_names_yes_no",
        ],
        "show_in_builder": True,
    },
    {
        "id": "organisation-charitable-objects",
        "builder_display_name": "Organisation Charitable objects",
        "form_display_name": "Organisation charitable objects",
        "component_names": ["reuse-charitable-objects"],
        "show_in_builder": True,
    },
    {
        "id": "alternative-organisation-name",
        "builder_display_name": "Alternative Organisation Names",
        "form_display_name": "Alternative names of your organisation",
        "component_names": [
            "reuse-alt-org-name-1",
            "reuse-alt-org-name-2",
            "reuse-alt-org-name-3",
        ],
        "show_in_builder": False,
    },
]


@pytest.mark.parametrize(
    "input_page, exp_result",
    [
        (
            Page(
                page_id=uuid4(),
                form_id=uuid4(),
                display_path="organisation-single-name",
                name_in_apply_json={"en": "Organisation Name"},
                form_index=1,
                components=[mock_c_1],
            ),
            {
                "path": "/organisation-single-name",
                "title": "Organisation Name",
                "components": [
                    {
                        "name": "organisation_name",
                        "options": {},
                        "type": "TextField",
                        "title": "Organisation name",
                        "hint": "This must match your registered legal organisation name",
                        "schema": {},
                        "metadata": {},
                    }
                ],
                "next": [],
            },
        )
    ],
)
def test_build_page_and_components(input_page, exp_result):
    result = build_page(input_page)
    assert result == exp_result


def test_build_page_controller_specified():
    input_page: Page = Page(name_in_apply_json={"en": "Name in json"}, controller="startPageController")
    result_page = build_page(page=input_page)
    assert result_page
    assert result_page["controller"] == "startPageController"


def test_build_page_controller_not_specified():
    input_page: Page = Page(name_in_apply_json={"en": "Name in json"}, controller=None)
    result_page = build_page(page=input_page)
    assert result_page
    assert ("controller" in result_page) is False


@pytest.mark.parametrize(
    "input_page",
    [
        (
            Page(
                page_id=uuid4(),
                form_id=uuid4(),
                display_path="organisation-single-name",
                name_in_apply_json={"en": "Organisation Name"},
                form_index=1,
                components=[mock_c_1],
            )
        ),
        (
            Page(
                page_id=uuid4(),
                form_id=uuid4(),
                display_path="organisation-single-name",
                name_in_apply_json={"en": "Organisation Name"},
                form_index=1,
                components=[mock_c_1, mock_c_2],
            )
        ),
        (
            Page(
                page_id=uuid4(),
                form_id=uuid4(),
                display_path="organisation-single-name",
                name_in_apply_json={"en": "Organisation Name"},
                form_index=1,
                components=[],
            )
        ),
    ],
)
def test_build_page(input_page):
    with mock.patch("app.export_config.generate_form.build_component", new_value=lambda c: c) as mock_build_component:
        result_page = build_page(input_page)
        assert result_page
        assert mock_build_component.call_count == len(input_page.components)
        assert len(result_page["components"]) == len(input_page.components)


id = uuid4()
id2 = uuid4()


@pytest.mark.parametrize(
    "input_component, exp_results",
    [
        (
            Component(
                component_id=id,
                title="test_title",
                type=ComponentType.TEXT_FIELD,
                conditions=[
                    {
                        "name": "test_condition",
                        "display_name": "display name",
                        "operator": "is",
                        "value": {"type": "Value", "value": "yes", "display": "yes"},
                        "destination_page_path": "./who-knows",
                        "coordinator": None,
                    },
                ],
                runner_component_name="test_name",
            ),
            [
                {
                    "displayName": "display name",
                    "name": "test_condition",
                    "value": {
                        "name": "display name",
                        "conditions": [
                            {
                                "field": {"name": "test_name", "type": "TextField", "display": "test_title"},
                                "operator": "is",
                                "value": {"type": "Value", "value": "yes", "display": "yes"},
                            }
                        ],
                    },
                }
            ],
        ),
        (
            Component(
                component_id=id2,
                title="test_title_2",
                type=ComponentType.TEXT_FIELD,
                conditions=[
                    {
                        "name": "test_condition",
                        "display_name": "display name",
                        "operator": "is",
                        "value": {"type": "Value", "value": "yes", "display": "yes"},
                        "destination_page_path": "./who-knows",
                    },
                    {
                        "name": "test_condition2",
                        "display_name": "display name",
                        "operator": "is",
                        "value": {"type": "Value", "value": "no", "display": "no"},
                        "destination_page_path": "./who-knows2",
                    },
                ],
                runner_component_name="test_name",
            ),
            [
                {
                    "displayName": "display name",
                    "name": "test_condition",
                    "value": {
                        "name": "display name",
                        "conditions": [
                            {
                                "field": {"name": "test_name", "type": "TextField", "display": "test_title_2"},
                                "operator": "is",
                                "value": {"type": "Value", "value": "yes", "display": "yes"},
                            }
                        ],
                    },
                },
                {
                    "displayName": "display name",
                    "name": "test_condition2",
                    "value": {
                        "name": "display name",
                        "conditions": [
                            {
                                "field": {"name": "test_name", "type": "TextField", "display": "test_title_2"},
                                "operator": "is",
                                "value": {"type": "Value", "value": "no", "display": "no"},
                            }
                        ],
                    },
                },
            ],
        ),
    ],
)
def test_build_conditions(input_component, exp_results):
    results = build_conditions(input_component)
    assert results == exp_results


list_id = uuid4()


@pytest.mark.parametrize(
    "component_to_build, exp_result",
    [
        (
            Component(
                component_id=uuid4(),
                type=ComponentType.TEXT_FIELD,
                title="Test Title",
                hint_text="This must be a hint",
                page_id=None,
                page_index=1,
                theme_id=None,
                runner_component_name="test-name",
                options={
                    "hideTitle": False,
                    "classes": "govuk-!-width-full",
                },
            ),
            {
                "name": "test-name",
                "options": {
                    "hideTitle": False,
                    "classes": "govuk-!-width-full",
                },
                "type": "TextField",
                "title": "Test Title",
                "hint": "This must be a hint",
                "schema": {},
                "metadata": {},
            },
        ),
        (
            Component(
                component_id=uuid4(),
                type=ComponentType.TEXT_FIELD,
                title="Test Title",
                hint_text="This must be a hint",
                page_id=None,
                page_index=1,
                theme_id=None,
                runner_component_name="test-name",
                options={},
                lizt=Lizt(name="test-list", list_id=list_id),
            ),
            {
                "name": "test-name",
                "options": {},
                "type": "TextField",
                "title": "Test Title",
                "hint": "This must be a hint",
                "schema": {},
                "metadata": {"fund_builder_list_id": str(list_id)},
                "list": "test-list",
            },
        ),
    ],
)
def test_build_component(component_to_build, exp_result):
    result = build_component(component=component_to_build)
    assert result == exp_result


@pytest.mark.parametrize(
    "input_pages,input_partial_json, exp_next",
    [
        # Simple flow of 1 page then summary (summary not in input pages)
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-single-name",
                    name_in_apply_json={"en": "Organisation Name"},
                    form_index=1,
                )
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-single-name",
                        "title": "Organisation Name",
                        "components": [
                            {
                                "name": "reuse-organisation-name",
                                "options": {
                                    "hideTitle": False,
                                    "classes": "govuk-!-width-full",
                                },
                                "type": "TextField",
                                "title": "Organisation name",
                                "hint": "This must match your registered legal organisation name",
                                "schema": {},
                            }
                        ],
                        "next": [],
                        "options": {},
                    },
                ],
            },
            {
                "/organisation-single-name": [{"path": "/summary"}],
            },
        ),
        # 1 page then summary (summary is in input pages)
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-single-name",
                    name_in_apply_json={"en": "Organisation Name"},
                    form_index=1,
                    default_next_page_id="summary-id",
                ),
                Page(
                    page_id="summary-id",
                    form_id=uuid4(),
                    display_path="summary-page",
                    name_in_apply_json={"en": "Summary Page"},
                    form_index=1,
                    controller="summary.js",
                ),
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-single-name",
                        "title": "Organisation Name",
                        "components": [
                            {
                                "name": "reuse-organisation-name",
                                "options": {
                                    "hideTitle": False,
                                    "classes": "govuk-!-width-full",
                                },
                                "type": "TextField",
                                "title": "Organisation name",
                                "hint": "This must match your registered legal organisation name",
                                "schema": {},
                            }
                        ],
                        "next": [],
                        "options": {},
                    },
                    {
                        "path": "/summary-page",
                        "title": "Summary Page",
                        "components": [],
                        "next": [],
                        "options": {},
                        "controller": "summary.js",
                    },
                ],
            },
            {
                "/organisation-single-name": [{"path": "/summary-page"}],
                "/summary-page": [],
            },
        ),
        # Simple flow of 2 pages then summary
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-single-name",
                    name_in_apply_json={"en": "Organisation Name"},
                    form_index=1,
                    default_next_page_id=id2,
                ),
                Page(
                    page_id=id2,
                    form_id=uuid4(),
                    display_path="organisation-charitable-objects",
                    name_in_apply_json={"en": "What are your organisation's charitable objects?"},
                    form_index=1,
                ),
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-single-name",
                        "title": "Organisation Name",
                        "components": [
                            {
                                "name": "reuse-organisation-name",
                                "options": {
                                    "hideTitle": False,
                                    "classes": "govuk-!-width-full",
                                },
                                "type": "TextField",
                                "title": "Organisation name",
                                "hint": "This must match your registered legal organisation name",
                                "schema": {},
                            },
                        ],
                        "next": [],
                        "options": {},
                    },
                    {
                        "path": "/organisation-charitable-objects",
                        "title": "Organisation Charitable Objects",
                        "components": [
                            {
                                "name": "reuse-charitable-objects",
                                "options": {"hideTitle": True, "maxWords": "500"},
                                "type": "FreeTextField",
                                "title": "What are your organisation's charitable objects?",
                                "hint": "You can find this in your organisation's governing document.",
                            },
                        ],
                        "next": [],
                        "options": {},
                    },
                ],
            },
            {
                "/organisation-single-name": [{"path": "/organisation-charitable-objects"}],
                "/organisation-charitable-objects": [{"path": "/summary"}],
            },
        ),
        # Just a summary page
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="summary",
                    name_in_apply_json={"en": "Summary"},
                    form_index=1,
                    controller="summary.js",
                )
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/summary",
                        "title": "Summary",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                ],
            },
            {
                "/summary": [],
            },
        ),
    ],
)
def test_build_navigation_no_conditions(input_partial_json, input_pages, exp_next):

    results = build_navigation(partial_form_json=input_partial_json, input_pages=input_pages)
    for page in results["pages"]:
        exp_next_this_page = exp_next[page["path"]]
        assert page["next"] == exp_next_this_page
    assert len(results["conditions"]) == 0


@pytest.mark.parametrize(
    "input_pages,input_partial_json ,exp_next, exp_conditions",
    [
        # One page, 2 possible nexts, both based on defined conditions
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-name",
                    name_in_apply_json={"en": "Organisation Name"},
                    form_index=1,
                    components=[
                        Component(
                            component_id=id2,
                            title="test_title_2",
                            type=ComponentType.TEXT_FIELD,
                            conditions=[
                                {
                                    "name": "orgno",
                                    "display_name": "organisation_other_names_no",
                                    "value": {"type": "Value", "value": "no", "display": "no"},
                                    "destination_page_path": "summary",
                                    "operator": "is",
                                    "coordinator": None,
                                },
                                {
                                    "name": "orgyes",
                                    "display_name": "organisation_other_names_yes",
                                    "operator": "is",
                                    "value": {"type": "Value", "value": "yes", "display": "yes"},
                                    "destination_page_path": "organisation-alternative-names",
                                    "coordinator": None,
                                },
                            ],
                            runner_component_name="test_c_1",
                        )
                    ],
                ),
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-alternative-names",
                    name_in_apply_json={"en": "Organisation Alternative Names"},
                    form_index=2,
                ),
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-name",
                        "title": "Organisation Name",
                        "components": [
                            {},  # don't care about these right now...
                            {},
                        ],
                        "next": [],
                        "options": {},
                    },
                    {
                        "path": "/organisation-alternative-names",
                        "title": "Organisation Alternative Names",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                ],
            },
            {
                "/organisation-name": [
                    {
                        "path": "/summary",
                        "condition": "orgno",
                    },
                    {
                        "path": "/organisation-alternative-names",
                        "condition": "orgyes",
                    },
                ],
                "/organisation-alternative-names": [{"path": "/summary"}],
            },
            [
                {
                    "displayName": "organisation_other_names_no",
                    "name": "orgno",
                    "value": {
                        "name": "organisation_other_names_no",
                        "conditions": [
                            {
                                "field": {
                                    "name": "test_c_1",
                                    "type": "TextField",
                                    "display": "test_title_2",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "no",
                                    "display": "no",
                                },
                            }
                        ],
                    },
                },
                {
                    "displayName": "organisation_other_names_yes",
                    "name": "orgyes",
                    "value": {
                        "name": "organisation_other_names_yes",
                        "conditions": [
                            {
                                "field": {
                                    "name": "test_c_1",
                                    "type": "TextField",
                                    "display": "test_title_2",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "yes",
                                    "display": "yes",
                                },
                            }
                        ],
                    },
                },
            ],
        ),
        # One page, 2 possible nexts, based on a condition and a default
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-name",
                    name_in_apply_json={"en": "Organisation Name"},
                    form_index=1,
                    components=[
                        Component(
                            component_id=id2,
                            title="test_title_2",
                            type=ComponentType.TEXT_FIELD,
                            conditions=[
                                {
                                    "name": "organisation_other_names_yes",
                                    "operator": "is",
                                    "value": "yes",
                                    "destination_page_path": "organisation-alternative-names",
                                },
                            ],
                            runner_component_name="test_c_1",
                        )
                    ],
                    default_next_page_id="summary-id",
                ),
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-alternative-names",
                    name_in_apply_json={"en": "Organisation Alternative Names"},
                    form_index=2,
                ),
                Page(
                    page_id="summary-id",
                    form_id=uuid4(),
                    display_path="summary-page",
                    name_in_apply_json={"en": "Summary Page"},
                    form_index=1,
                    controller="summary.js",
                ),
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-name",
                        "title": "Organisation Name",
                        "components": [
                            {},  # don't care about these right now...
                            {},
                        ],
                        "next": [],
                        "options": {},
                    },
                    {
                        "path": "/organisation-alternative-names",
                        "title": "Organisation Alternative Names",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                    {
                        "path": "/summary-page",
                        "title": "Summary Page",
                        "components": [],
                        "next": [],
                        "options": {},
                        "controller": "summary.js",
                    },
                ],
            },
            {
                "/organisation-name": [
                    {
                        "path": "/summary-page",
                    },
                    {
                        "path": "/organisation-alternative-names",
                        "condition": "organisation_other_names_yes",
                    },
                ],
                "/organisation-alternative-names": [{"path": "/summary"}],
                "/summary-page": [],
            },
            [
                {
                    "displayName": "organisation_other_names_yes",
                    "name": "organisation_other_names_yes",
                    "value": {
                        "name": "organisation_other_names_yes",
                        "conditions": [
                            {
                                "field": {
                                    "name": "test_c_1",
                                    "type": "TextField",
                                    "display": "test_title_2",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "yes",
                                    "display": "yes",
                                },
                            }
                        ],
                    },
                },
            ],
        ),
        # TODO One page, 3 possible nexts based on complex conditions (coordinators)
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-type",
                    name_in_apply_json={"en": "Organisation Type"},
                    form_index=1,
                    components=[
                        Component(
                            component_id=id2,
                            title="org_type",
                            type=ComponentType.RADIOS_FIELD,
                            conditions=[
                                {
                                    "name": "org_type_a",
                                    "operator": "is",
                                    "value": "A1",
                                    "destination_page_path": "org-type-a",
                                },
                                {
                                    "name": "org_type_b",
                                    "operator": "is",
                                    "value": "B1",
                                    "destination_page_path": "org-type-b",
                                },
                                # TODO combine these 2 using coordinators after Adam's change
                                {
                                    "name": "org_type_c",
                                    "operator": "is",
                                    "value": "C1",
                                    "destination_page_path": "org-type-c",
                                },
                                {
                                    "name": "org_type_c",
                                    "operator": "is",
                                    "value": "C2",
                                    "destination_page_path": "org-type-c",
                                },
                            ],
                            runner_component_name="org_type_component",
                        )
                    ],
                ),
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="org-type-a",
                    name_in_apply_json={"en": "Organisation Type A"},
                    form_index=2,
                ),
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="org-type-b",
                    name_in_apply_json={"en": "Organisation Type B"},
                    form_index=2,
                ),
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="org-type-c",
                    name_in_apply_json={"en": "Organisation Type C"},
                    form_index=2,
                ),
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-type",
                        "title": "Organisation Type",
                        "components": [
                            {},  # don't care about these right now...
                            {},
                        ],
                        "next": [],
                        "options": {},
                    },
                    {
                        "path": "/org-type-a",
                        "title": "org-type-a",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                    {
                        "path": "/org-type-b",
                        "title": "org-type-b",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                    {
                        "path": "/org-type-c",
                        "title": "org-type-c",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                ],
            },
            {
                "/organisation-type": [
                    {
                        "path": "/org-type-a",
                        "condition": "org-type-a",
                    },
                    {
                        "path": "/org-type-b",
                        "condition": "org-type-b",
                    },
                    {
                        "path": "/org-type-c",
                        "condition": "org-type-c",
                    },
                ],
                "/org-type-a": [{"path": "/summary"}],
                "/org-type-b": [{"path": "/summary"}],
                "/org-type-c": [{"path": "/summary"}],
            },
            [
                {
                    "displayName": "org-type-a",
                    "name": "org-type-a",
                    "value": {
                        "name": "org-type-a",
                        "conditions": [
                            {
                                "field": {
                                    "name": "org_type_component",
                                    "type": "RadiosField",
                                    "display": "org_type",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "A",
                                    "display": "A",
                                },
                            },
                        ],
                    },
                },
                {
                    "displayName": "org-type-b",
                    "name": "org-type-b",
                    "value": {
                        "name": "org-type-b",
                        "conditions": [
                            {
                                "field": {
                                    "name": "org_type_component",
                                    "type": "RadiosField",
                                    "display": "org_type",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "B",
                                    "display": "B",
                                },
                            },
                        ],
                    },
                },
                {
                    "displayName": "org-type-c",
                    "name": "org-type-c",
                    "value": {
                        "name": "org-type-c",
                        "conditions": [
                            {
                                "field": {
                                    "name": "org_type_component",
                                    "type": "RadiosField",
                                    "display": "org_type",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "C1",
                                    "display": "C1",
                                },
                            },
                            {
                                "coordinator": "or",
                                "field": {
                                    "name": "org_type_component",
                                    "type": "RadiosField",
                                    "display": "org_type",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "C2",
                                    "display": "C2",
                                },
                            },
                        ],
                    },
                },
            ],
        ),
    ],
)
def test_build_navigation_with_conditions(mocker, input_pages, input_partial_json, exp_next, exp_conditions):
    mocker.patch(
        "app.export_config.generate_form.build_page",
        return_value={"path": "/organisation-alternative-names", "next": []},
    )
    results = build_navigation(partial_form_json=input_partial_json, input_pages=input_pages)
    for page in results["pages"]:
        exp_next_this_page = exp_next[page["path"]]
        assert page["next"] == exp_next_this_page
    assert results["conditions"] == exp_conditions


@pytest.mark.parametrize(
    "input_form, exp_results",
    [
        (
            mock_form_1,
            {
                "startPage": "/intro-a-test-form",
                "pages": [
                    {
                        "path": "/intro-a-test-form",
                        "title": "A test form",
                        "next": [{"path": "/test-display-path"}],
                    },
                    {
                        "path": "/test-display-path",
                        "title": "A test page",
                        "next": [
                            {
                                "path": "/summary",
                            },
                        ],
                        "exp_component_count": 2,
                    },
                    {
                        "path": "/summary",
                        "title": "Check your answers",
                        "next": [],
                        "exp_component_count": 0,
                    },
                ],
            },
        ),
    ],
)
def test_build_form(input_form, exp_results):
    results = build_form_json(form=input_form)
    assert results
    assert len(results["pages"]) == len(exp_results["pages"])
    assert results["name"] == input_form.name_in_apply_json["en"]
    for exp_page in exp_results["pages"]:
        result_page = next((res_page for res_page in results["pages"] if res_page["path"] == exp_page["path"]), None)
        assert result_page, f"{exp_page['path']}"
        assert result_page["title"] == exp_page["title"]
        if "exp_component_count" in exp_page:
            assert len(result_page["components"]) == exp_page["exp_component_count"]
        if "next" in exp_page:
            for exp_next in exp_page["next"]:
                assert exp_next["path"] in [next["path"] for next in result_page["next"]]
                if "condition" in exp_next:
                    assert exp_next["condition"] in [next["condition"] for next in result_page["next"]]
