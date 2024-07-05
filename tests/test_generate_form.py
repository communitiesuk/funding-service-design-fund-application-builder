from uuid import uuid4

import pytest

from app.db.models import Page

# from app.question_reuse.generate_form import build_conditions
from app.question_reuse.generate_form import build_form_json
from app.question_reuse.generate_form import build_lists
from app.question_reuse.generate_form import build_navigation
from app.question_reuse.generate_form import build_page
from tests.unit_test_data import *

LIST1 = {
    "type": "string",
    "items": [{"text": "Hello", "value": "h"}, {"text": "goodbye", "value": "g"}],
}


@pytest.mark.parametrize(
    "pages, available_lists, exp_result",
    [
        (
            [{"components": [{"title": "First component", "list": "list1"}]}],
            {"list1": LIST1},
            [LIST1],
        ),
        (
            [
                {
                    "components": [
                        {"title": "First component", "list": "list1"},
                        {"title": "Second component", "list": "list1"},
                    ]
                }
            ],
            {"list1": LIST1},
            [LIST1, LIST1],
        ),
    ],
)
def test_build_lists(mocker, pages, available_lists, exp_result):
    mocker.patch("app.data.data_access.LISTS", available_lists)
    results = build_lists(pages)
    assert len(results) == len(exp_result)


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
                name_in_apply={"en": "Organisation Name"},
                form_index=1,
                components=[mock_c_1],
            ),
            {
                "path": "/organisation-single-name",
                "title": "Organisation Name",
                "components": [
                    {
                        "name": str(mock_c_1.component_id),
                        "options": {},
                        "type": "TextField",
                        "title": "Organisation name",
                        "hint": "This must match your registered legal organisation name",
                        "schema": {},
                    }
                ],
                "next": [],
                "options": {},
            },
        )
    ],
)
def test_build_page(mocker, input_page, exp_result):
    result = build_page(input_page)
    assert result == exp_result


@pytest.mark.parametrize(
    "input_name, input_component, exp_results",
    [
        (
            "test_component",
            {
                "conditions": [
                    {"name": "test_condition", "operator": "is", "value": "yes"},
                ],
                "json_snippet": {
                    "type": "test_type",
                    "title": "test_title",
                },
            },
            [
                {
                    "displayName": "test_condition",
                    "name": "test_condition",
                    "value": {
                        "name": "test_condition",
                        "conditions": [
                            {
                                "field": {
                                    "name": "test_component",
                                    "type": "test_type",
                                    "display": "test_title",
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
                }
            ],
        ),
        (
            "test_component2",
            {
                "conditions": [
                    {"name": "test_condition", "operator": "is", "value": "yes"},
                    {"name": "test_condition2", "operator": "is", "value": "no"},
                ],
                "json_snippet": {
                    "type": "test_type",
                    "title": "test_title",
                },
            },
            [
                {
                    "displayName": "test_condition",
                    "name": "test_condition",
                    "value": {
                        "name": "test_condition",
                        "conditions": [
                            {
                                "field": {
                                    "name": "test_component2",
                                    "type": "test_type",
                                    "display": "test_title",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "yes",
                                    "display": "yes",
                                },
                            },
                        ],
                    },
                },
                {
                    "displayName": "test_condition2",
                    "name": "test_condition2",
                    "value": {
                        "name": "test_condition2",
                        "conditions": [
                            {
                                "field": {
                                    "name": "test_component2",
                                    "type": "test_type",
                                    "display": "test_title",
                                },
                                "operator": "is",
                                "value": {
                                    "type": "Value",
                                    "value": "no",
                                    "display": "no",
                                },
                            },
                        ],
                    },
                },
            ],
        ),
    ],
)
def test_build_conditions(input_name, input_component, exp_results):
    assert False, "Rewrite conditions stuff"
    # results = build_conditions(input_name, input_component)
    # assert results == exp_results


@pytest.mark.parametrize(
    "input_pages,input_partial_json, exp_next",
    [
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-single-name",
                    name_in_apply={"en": "Organisation Name"},
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
        (
            [
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-single-name",
                    name_in_apply={"en": "Organisation Name"},
                    form_index=1,
                ),
                Page(
                    page_id=uuid4(),
                    form_id=uuid4(),
                    display_path="organisation-charitable-objects",
                    name_in_apply={"en": "What are your organisation's charitable objects?"},
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
    ],
)
def test_build_navigation_no_conditions(mocker, input_partial_json, input_pages, exp_next):

    results = build_navigation(partial_form_json=input_partial_json, input_pages=input_pages)
    for page in results["pages"]:
        exp_next_this_page = exp_next[page["path"]]
        assert page["next"] == exp_next_this_page
    assert len(results["conditions"]) == 0


@pytest.mark.parametrize(
    "page_names,pages ,exp_next, exp_conditions",
    [
        (
            ["organisation-name", "organisation-charitable-objects"],
            {
                "conditions": [],
                "pages": [
                    {
                        "path": "/organisation-name",
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
                            {
                                "name": "reuse_organisation_other_names_yes_no",
                                "options": {},
                                "type": "YesNoField",
                                "title": "Does your organisation use any other names?",
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
                "/organisation-name": [
                    {
                        "path": "/organisation-charitable-objects",
                        "condition": "organisation_other_names_no",
                    },
                    {
                        "path": "/alternative-organisation-name",
                        "condition": "organisation_other_names_yes",
                    },
                ],
                "/organisation-charitable-objects": [{"path": "/summary"}],
                "/alternative-organisation-name": [{"path": "/organisation-charitable-objects"}],
            },
            {},
        )
    ],
)
def test_build_navigation_with_conditions(mocker, pages, page_names, exp_next, exp_conditions):
    mocker.patch("app.data.data_access.COMPONENTS", mock_components)
    mocker.patch("app.data.data_access.PAGES", mock_pages)
    assert False, "Rewrite with conditions stuff"
    # results = build_navigation(pages, page_names)
    # for page in results["pages"]:
    #     exp_next_this_page = exp_next[page["path"]]
    #     for next in page["next"]:
    #         assert next in exp_next_this_page


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
    assert results["name"] == input_form.name_in_apply["en"]
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
