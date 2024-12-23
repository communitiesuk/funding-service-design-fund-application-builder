from copy import deepcopy
from dataclasses import asdict
from unittest import mock
from uuid import uuid4

import pytest

from app.db.models import Component, ComponentType, FormSection, Lizt, Page
from app.db.models.application_config import Form
from app.export_config.generate_form import (
    build_component,
    build_conditions,
    build_form_json,
    build_form_section,
    build_lists,
    build_navigation,
    build_page,
    build_start_page,
    human_to_kebab_case,
)
from tests.unit_test_data import (
    mock_c_1,
    mock_c_2,
    mock_form_1,
    test_condition_org_type_a,
    test_condition_org_type_b,
    test_condition_org_type_c,
    test_form_json_condition_org_type_a,
    test_form_json_condition_org_type_b,
    test_form_json_condition_org_type_c,
    test_form_json_page_org_type_a,
    test_form_json_page_org_type_b,
    test_form_json_page_org_type_c,
    test_page_object_org_type_a,
    test_page_object_org_type_b,
    test_page_object_org_type_c,
)


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
        (
            Page(
                page_id=uuid4(),
                form_id=uuid4(),
                display_path="page-with-options",
                name_in_apply_json={"en": "Page with Options Name"},
                form_index=1,
                components=[],
                options={"first": "option"},
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
        if input_page.options:
            assert result_page["options"] == input_page.options


id = uuid4()
id2 = uuid4()


@pytest.mark.parametrize(
    "input_component, exp_results",
    [
        # single condition
        (
            Component(
                component_id=id,
                title="org type",
                type=ComponentType.TEXT_FIELD,
                conditions=[
                    asdict(test_condition_org_type_a),
                ],
                runner_component_name="org_type",
            ),
            [test_form_json_condition_org_type_a],
        ),
        # 2 conditions
        (
            Component(
                component_id=id2,
                title="test_title_2",
                type=ComponentType.TEXT_FIELD,
                conditions=[
                    asdict(test_condition_org_type_a),
                    asdict(test_condition_org_type_b),
                ],
                runner_component_name="test_name",
            ),
            [
                test_form_json_condition_org_type_a,
                test_form_json_condition_org_type_b,
            ],
        ),
        # single complex condition
        (
            Component(
                component_id=id2,
                title="test_title_2",
                type=ComponentType.TEXT_FIELD,
                conditions=[asdict(test_condition_org_type_c)],
                runner_component_name="test_name",
            ),
            [
                test_form_json_condition_org_type_c,
            ],
        ),
    ],
)
def test_build_conditions(input_component, exp_results, ids=None):
    if ids is None:
        ids = ["single condition", "2 conditions", "single condition with coordinator"]
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
                type=ComponentType.LIST_FIELD,
                title="Test Title",
                hint_text="This must be a hint",
                page_id=None,
                page_index=1,
                theme_id=None,
                runner_component_name="test-name",
                options={},
                lizt=Lizt(name="test-list", list_id=list_id),
                list_id=list_id,
            ),
            {
                "name": "test-name",
                "options": {},
                "type": "List",
                "title": "Test Title",
                "hint": "This must be a hint",
                "schema": {},
                "metadata": {"fund_builder_list_id": str(list_id)},
                "list": "test-list",
                "values": {"type": "listRef"},
            },
        ),
        (
            Component(
                component_id=uuid4(),
                type=ComponentType.MULTI_INPUT_FIELD,
                title="Test Title",
                hint_text="This must be a hint",
                page_id=None,
                page_index=1,
                theme_id=None,
                runner_component_name="test-name",
                options={},
                lizt=None,
                list_id=None,
                children=[
                    {"name": "GLQlOh", "options": {}, "type": "TextField", "title": "Describe the cost"},
                    {
                        "name": "JtwkMy",
                        "options": {"prefix": "£", "classes": "govuk-!-width-one-half"},
                        "type": "NumberField",
                        "title": "Amount",
                        "hint": "",
                        "schema": {},
                    },
                    {
                        "name": "LeTLDo",
                        "options": {"prefix": "£", "classes": "govuk-!-width-one-half"},
                        "type": "NumberField",
                        "title": "How much money from the COF25 grant will you use to pay for this cost?",
                        "hint": "",
                        "schema": {},
                    },
                    {
                        "name": "pHZDWT",
                        "options": {"prefix": "£", "classes": "govuk-!-width-one-half"},
                        "type": "NumberField",
                        "title": "How much of the match funding will you use to pay for this cost?",
                        "hint": "",
                        "schema": {},
                    },
                ],
            ),
            {
                "name": "test-name",
                "options": {},
                "type": "MultiInputField",
                "title": "Test Title",
                "hint": "This must be a hint",
                "schema": {},
                "metadata": {},
                "children": [
                    {"name": "GLQlOh", "options": {}, "type": "TextField", "title": "Describe the cost"},
                    {
                        "name": "JtwkMy",
                        "options": {"prefix": "£", "classes": "govuk-!-width-one-half"},
                        "type": "NumberField",
                        "title": "Amount",
                        "hint": "",
                        "schema": {},
                    },
                    {
                        "name": "LeTLDo",
                        "options": {"prefix": "£", "classes": "govuk-!-width-one-half"},
                        "type": "NumberField",
                        "title": "How much money from the COF25 grant will you use to pay for this cost?",
                        "hint": "",
                        "schema": {},
                    },
                    {
                        "name": "pHZDWT",
                        "options": {"prefix": "£", "classes": "govuk-!-width-one-half"},
                        "type": "NumberField",
                        "title": "How much of the match funding will you use to pay for this cost?",
                        "hint": "",
                        "schema": {},
                    },
                ],
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
    "input_pages,input_partial_json ,exp_next",
    [
        # One page, 2 possible nexts, both based on defined conditions
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
                                asdict(test_condition_org_type_c),
                                asdict(test_condition_org_type_b),
                            ],
                            runner_component_name="test_c_1",
                        )
                    ],
                ),
                test_page_object_org_type_b,
                test_page_object_org_type_c,
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-type",
                        "title": "Organisation Type",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                    deepcopy(test_form_json_page_org_type_b),
                    deepcopy(test_form_json_page_org_type_c),
                ],
            },
            {
                "/organisation-type": [
                    {
                        "path": "/org-type-c",
                        "condition": "org_type_c",
                    },
                    {
                        "path": "/org-type-b",
                        "condition": "org_type_b",
                    },
                ],
                "/org-type-b": [{"path": "/summary"}],
                "/org-type-c": [{"path": "/summary"}],
            },
        ),
        # One page, 2 possible nexts, based on a condition and a default (summary)
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-type",
                    name_in_apply_json={"en": "Organisation Type"},
                    form_index=1,
                    default_next_page_id="summary-id",
                    components=[
                        Component(
                            component_id=id2,
                            title="org_type",
                            type=ComponentType.RADIOS_FIELD,
                            conditions=[
                                asdict(test_condition_org_type_b),
                            ],
                            runner_component_name="test_c_1",
                        )
                    ],
                ),
                test_page_object_org_type_b,
                Page(
                    page_id="summary-id",
                    form_id=uuid4(),
                    display_path="summary",
                    name_in_apply_json={"en": "Summary"},
                    form_index=2,
                    controller="summary.js",
                ),
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-type",
                        "title": "Organisation Type",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                    deepcopy(test_form_json_page_org_type_b),
                    {
                        "path": "/summary",
                        "title": "Summary",
                        "components": [],
                        "next": [],
                        "options": {},
                        "controller": "summary.js",
                    },
                ],
            },
            {
                "/organisation-type": [
                    {
                        "path": "/summary",
                    },
                    {
                        "path": "/org-type-b",
                        "condition": "org_type_b",
                    },
                ],
                "/org-type-b": [{"path": "/summary"}],
                "/summary": [],
            },
        ),  # One page, 2 possible nexts, based on a condition and a default
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-type",
                    name_in_apply_json={"en": "Organisation Type"},
                    form_index=1,
                    default_next_page_id="page-2",
                    components=[
                        Component(
                            component_id=id2,
                            title="org_type",
                            type=ComponentType.RADIOS_FIELD,
                            conditions=[
                                asdict(test_condition_org_type_b),
                            ],
                            runner_component_name="test_c_1",
                        )
                    ],
                ),
                test_page_object_org_type_b,
                Page(
                    page_id="page-2",
                    form_id=uuid4(),
                    display_path="page_2",
                    name_in_apply_json={"en": "Page 2"},
                    form_index=2,
                ),
            ],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-type",
                        "title": "Organisation Type",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                    deepcopy(test_form_json_page_org_type_b),
                    {
                        "path": "/page_2",
                        "title": "Page 2",
                        "components": [],
                        "next": [],
                        "options": {},
                    },
                ],
            },
            {
                "/organisation-type": [
                    {
                        "path": "/page_2",
                    },
                    {
                        "path": "/org-type-b",
                        "condition": "org_type_b",
                    },
                ],
                "/org-type-b": [{"path": "/summary"}],
                "/page_2": [{"path": "/summary"}],
                "/summary": [],
            },
        ),
        # # One page, 3 possible nexts based on complex conditions (coordinators)
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
                                asdict(test_condition_org_type_a),
                                asdict(test_condition_org_type_b),
                                asdict(test_condition_org_type_c),
                            ],
                            runner_component_name="org_type_component",
                        )
                    ],
                ),
                test_page_object_org_type_a,
                test_page_object_org_type_b,
                test_page_object_org_type_c,
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
                    deepcopy(test_form_json_page_org_type_a),
                    deepcopy(test_form_json_page_org_type_b),
                    deepcopy(test_form_json_page_org_type_c),
                ],
            },
            {
                "/organisation-type": [
                    {
                        "path": "/org-type-a",
                        "condition": "org_type_a",
                    },
                    {
                        "path": "/org-type-b",
                        "condition": "org_type_b",
                    },
                    {
                        "path": "/org-type-c",
                        "condition": "org_type_c",
                    },
                ],
                "/org-type-a": [{"path": "/summary"}],
                "/org-type-b": [{"path": "/summary"}],
                "/org-type-c": [{"path": "/summary"}],
            },
        ),
    ],
)
def test_build_navigation_with_conditions(mocker, input_pages, input_partial_json, exp_next):
    mocker.patch("app.export_config.generate_form.build_conditions", return_value=["mock list"])
    results = build_navigation(partial_form_json=input_partial_json, input_pages=input_pages)
    for page in results["pages"]:
        exp_next_this_page = exp_next[page["path"]]
        assert page["next"] == exp_next_this_page, f"next for page {page['path']} does not match expected"
    assert results["conditions"] == ["mock list"]


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
    assert results["name"] == "Access Funding"
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


@pytest.mark.parametrize(
    "input_content, input_form, expected_title, expected_path, expected_next, expected_content",
    [
        (
            "2 pages",
            Form(
                name_in_apply_json={"en": "Test Form"},
                pages=[
                    Page(name_in_apply_json={"en": "Page 1"}, display_path="page-1"),
                    Page(name_in_apply_json={"en": "Page 2"}, display_path="page-2"),
                ],
            ),
            "Test Form",
            "/intro-test-form",
            [{"path": "/page-1"}],
            (
                '<p class="govuk-body">2 pages</p>'
                '<p class="govuk-body">We will ask you about:</p> <ul>'
                "<li>Page 1</li><li>Page 2</li></ul>"
            ),
        ),
        (
            "Single page",
            Form(
                name_in_apply_json={"en": "Another Form"},
                pages=[Page(name_in_apply_json={"en": "Details Page"}, display_path="details-page")],
            ),
            "Another Form",
            "/intro-another-form",
            [{"path": "/details-page"}],
            (
                '<p class="govuk-body">Single page</p>'
                '<p class="govuk-body">We will ask you about:</p> <ul>'
                "<li>Details Page</li></ul>"
            ),
        ),
        (
            "Form with no pages",
            Form(name_in_apply_json={"en": "Another Form"}, pages=[]),
            "Another Form",
            "/intro-another-form",
            [],
            ('<p class="govuk-body">Form with no pages</p>'),
        ),
    ],
)
def test_build_start_page(input_content, input_form, expected_title, expected_path, expected_next, expected_content):
    result = build_start_page(input_content, input_form)

    # Assert
    assert result["title"] == expected_title
    assert result["path"] == expected_path
    assert result["controller"] == "./pages/start.js"
    assert result["next"] == expected_next
    assert result["components"][0]["content"] == expected_content


@pytest.mark.parametrize(
    "input_form, sections_count",
    [(FormSection(name="test", title="Test section", hide_title=False), 1)],
)
def test_build_form_sections(input_form, sections_count):
    sections = []
    build_form_section(sections, input_form)
    assert len(sections) == sections_count
    assert sections[0]["title"] == "Test section"
    assert sections[0]["name"] == "test"
