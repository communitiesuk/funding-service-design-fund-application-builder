from uuid import uuid4

from app.db.models import (
    Form,
    Fund,
    Round,
    Section,
)
from app.shared.data_classes import Condition, ConditionValue
from tests.seed_test_data import BASIC_FUND_INFO, BASIC_ROUND_INFO

# Form JSONs based on the existing mock data
MOCK_FORM_JSON_SIMPLE = {
    "startPage": "/test-display-path",
    "pages": [
        {
            "path": "/test-display-path",
            "title": "A test page",
            "components": [
                {
                    "name": "organisation_name",
                    "options": {},
                    "type": "TextField",
                    "title": "Organisation name",
                    "hint": "This must match your registered legal organisation name",
                    "schema": {},
                },
                {
                    "name": "email-address",
                    "options": {},
                    "type": "EmailAddressField",
                    "title": "What is your email address?",
                    "hint": "Work not personal",
                    "schema": {},
                },
            ],
            "next": [{"path": "/summary"}],
        },
        {
            "path": "/summary",
            "title": "Check your answers",
            "components": [],
            "next": [],
            "controller": "./pages/summary.js",
        },
    ],
    "lists": [
        {
            "name": "greetings_list",
            "type": "string",
            "items": [{"text": "Hello", "value": "h"}, {"text": "Goodbye", "value": "g"}],
        }
    ],
    "conditions": [],
    "sections": [],
    "outputs": [],
    "skipSummary": False,
    "name": "A test form",
}

MOCK_FORM_JSON_WITH_CONDITIONS = {
    "startPage": "/organisation-type",
    "pages": [
        {
            "path": "/organisation-type",
            "title": "Organisation Type",
            "components": [
                {
                    "name": "org_type",
                    "options": {},
                    "type": "RadiosField",
                    "title": "org_type",
                    "list": "org_types_list",
                    "schema": {},
                }
            ],
            "next": [
                {"path": "/org-type-a", "condition": "org_type_a"},
                {"path": "/org-type-b", "condition": "org_type_b"},
                {"path": "/org-type-c", "condition": "org_type_c"},
                {"path": "/summary"},
            ],
        },
        {"path": "/org-type-a", "title": "Organisation Type A", "components": [], "next": [{"path": "/summary"}]},
        {"path": "/org-type-b", "title": "Organisation Type B", "components": [], "next": [{"path": "/summary"}]},
        {"path": "/org-type-c", "title": "Organisation Type C", "components": [], "next": [{"path": "/summary"}]},
        {
            "path": "/summary",
            "title": "Check your answers",
            "components": [],
            "next": [],
            "controller": "./pages/summary.js",
        },
    ],
    "lists": [
        {
            "name": "org_types_list",
            "type": "string",
            "items": [
                {"text": "Type A", "value": "A"},
                {"text": "Type B", "value": "B"},
                {"text": "Type C1", "value": "C1"},
                {"text": "Type C2", "value": "C2"},
            ],
        }
    ],
    "conditions": [
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
        {
            "displayName": "org type b",
            "name": "org_type_b",
            "value": {
                "name": "org type b",
                "conditions": [
                    {
                        "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                        "operator": "is",
                        "value": {"type": "Value", "value": "B", "display": "B"},
                    }
                ],
            },
        },
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
                        "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                        "operator": "is",
                        "value": {"type": "Value", "value": "C2", "display": "C2"},
                        "coordinator": "or",
                    },
                ],
            },
        },
    ],
    "sections": [],
    "outputs": [],
    "skipSummary": False,
    "name": "Organisation Type Form",
}

SEEDED_FORM_JSON = {
    "startPage": "/organisation-name",
    "pages": [
        {
            "path": "/organisation-name",
            "title": "Organisation Name",
            "components": [
                {
                    "name": "organisation_name",
                    "options": {"hideTitle": False, "classes": ""},
                    "type": "TextField",
                    "title": "What is your organisation's name?",
                    "hint": "This must match the regsitered legal organisation name",
                    "schema": {},
                },
                {
                    "name": "does_your_organisation_use_other_names",
                    "options": {"hideTitle": False, "classes": ""},
                    "type": "YesNoField",
                    "title": "Does your organisation use any other names?",
                    "schema": {},
                },
            ],
            "next": [
                {"path": "/organisation-alternative-names", "condition": "organisation_other_names_yes"},
                {"path": "/summary", "condition": "organisation_other_names_no"},
            ],
        },
        {
            "path": "/organisation-alternative-names",
            "title": "Alternative names of your organisation",
            "components": [
                {
                    "name": "alt_name_1",
                    "options": {"hideTitle": False, "classes": ""},
                    "type": "TextField",
                    "title": "Alternative Name 1",
                    "schema": {},
                }
            ],
            "next": [{"path": "/summary"}],
        },
        {
            "path": "/summary",
            "title": "Check your answers",
            "components": [],
            "next": [],
            "controller": "./pages/summary.js",
        },
    ],
    "lists": [],
    "conditions": [
        {
            "displayName": "org other names no",
            "name": "organisation_other_names_no",
            "value": {
                "name": "org other names no",
                "conditions": [
                    {
                        "field": {"name": "org_other_names", "type": "YesNoField", "display": "org other names"},
                        "operator": "is",
                        "value": {"type": "Value", "value": "false", "display": "false"},
                    }
                ],
            },
        },
        {
            "displayName": "org other names yes",
            "name": "organisation_other_names_yes",
            "value": {
                "name": "org other names yes",
                "conditions": [
                    {
                        "field": {"name": "org_other_names", "type": "YesNoField", "display": "org other names"},
                        "operator": "is",
                        "value": {"type": "Value", "value": "true", "display": "false"},
                    }
                ],
            },
        },
    ],
    "sections": [],
    "outputs": [],
    "skipSummary": False,
    "name": "About your organisation",
}

# IDs for the seeded form
mock_fund_id = uuid4()
mock_round_id = uuid4()
mock_section_id = uuid4()
mock_form_id = uuid4()

seeded_form = {
    "funds": [Fund(fund_id=mock_fund_id, short_name="UTFWC", **BASIC_FUND_INFO)],
    "rounds": [
        Round(
            round_id=mock_round_id,
            title_json={"en": "UT RWC"},
            fund_id=mock_fund_id,
            short_name="UTRWC",
            **BASIC_ROUND_INFO,
        )
    ],
    "sections": [
        Section(
            section_id=mock_section_id,
            index=1,
            round_id=mock_round_id,
            name_in_apply_json={"en": "Organisation Information"},
        )
    ],
    "forms": [
        Form(
            form_id=mock_form_id,
            section_id=mock_section_id,
            name_in_apply_json={"en": "About your organisation"},
            section_index=1,
            runner_publish_name="about-your-org",
            form_json=SEEDED_FORM_JSON,
        )
    ],
}

# Mock objects for tests that need individual components (converted to simpler form)
mock_section_1_id = uuid4()
mock_form_1_id = uuid4()

mock_section_1 = Section(
    section_id=mock_section_1_id,
    name_in_apply_json={"en": "Test Section 1"},
)

mock_form_1 = Form(
    form_id=mock_form_1_id,
    section_id=mock_section_1_id,
    name_in_apply_json={"en": "A test form"},
    runner_publish_name="a-test-form",
    section_index=1,
    form_json=MOCK_FORM_JSON_SIMPLE,
)

# Form with conditions for more complex tests
mock_form_with_conditions = Form(
    form_id=uuid4(),
    section_id=mock_section_1_id,
    name_in_apply_json={"en": "Organisation Type Form"},
    runner_publish_name="organisation-type-form",
    section_index=2,
    form_json=MOCK_FORM_JSON_WITH_CONDITIONS,
)

# Condition objects for tests that need them directly
test_condition_org_type_a = Condition(
    name="org_type_a",
    display_name="org type a",
    destination_page_path="/org-type-a",
    value=ConditionValue(
        name="org type a",
        conditions=[
            {
                "field": {
                    "name": "org_type",
                    "type": "RadiosField",
                    "display": "org type",
                },
                "operator": "is",
                "value": {"type": "Value", "value": "A", "display": "A"},
            }
        ],
    ),
)

test_condition_org_type_b = Condition(
    name="org_type_b",
    display_name="org type b",
    destination_page_path="/org-type-b",
    value=ConditionValue(
        name="org type b",
        conditions=[
            {
                "field": {
                    "name": "org_type",
                    "type": "RadiosField",
                    "display": "org type",
                },
                "operator": "is",
                "value": {"type": "Value", "value": "B", "display": "B"},
            }
        ],
    ),
)

test_condition_org_type_c = Condition(
    name="org_type_c",
    display_name="org type c",
    destination_page_path="/org-type-c",
    value=ConditionValue(
        name="org type c",
        conditions=[
            {
                "field": {
                    "name": "org_type",
                    "type": "RadiosField",
                    "display": "org type",
                },
                "operator": "is",
                "value": {"type": "Value", "value": "C1", "display": "C1"},
            },
            {
                "field": {
                    "name": "org_type",
                    "type": "RadiosField",
                    "display": "org type",
                },
                "operator": "is",
                "value": {"type": "Value", "value": "C2", "display": "C2"},
                "coordinator": "or",
            },
        ],
    ),
)

# JSON representations for tests that need them
test_form_json_condition_org_type_a = {
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
}

test_form_json_condition_org_type_b = {
    "displayName": "org type b",
    "name": "org_type_b",
    "value": {
        "name": "org type b",
        "conditions": [
            {
                "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                "operator": "is",
                "value": {"type": "Value", "value": "B", "display": "B"},
            }
        ],
    },
}

test_form_json_condition_org_type_c = {
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
}
