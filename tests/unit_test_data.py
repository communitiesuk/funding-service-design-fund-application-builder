from dataclasses import asdict
from uuid import uuid4

from app.db.models import (
    Component,
    ComponentType,
    Criteria,
    Form,
    Fund,
    Lizt,
    Page,
    PageCondition,
    Round,
    Section,
    Subcriteria,
    Theme,
)
from app.db.models import Condition as DbCondition
from app.shared.data_classes import Condition, ConditionValue
from tests.seed_test_data import BASIC_FUND_INFO, BASIC_ROUND_INFO

mock_section_1_id = uuid4()
mock_theme_1_id = uuid4()
mock_form_1_id = uuid4()
mock_page_1_id = uuid4()
mock_page_2_id = uuid4()
mock_page_3_condition_id = uuid4()
test_page_object_org_type_a_id = uuid4()
test_page_object_org_type_b_id = uuid4()
test_page_object_org_type_c_id = uuid4()
mock_page_4_condition_id = uuid4()
mock_component_1_id = uuid4()
mock_component_2_id = uuid4()
mock_component_3_id = uuid4()
mock_component_4_radio_field_2_id = uuid4()
mock_component_4_radio_field_3_id = uuid4()
mock_condition_1_id = uuid4()
mock_condition_2_id = uuid4()
mock_condition_3_id = uuid4()
mock_condition_4_id = uuid4()
mock_condition_5_id = uuid4()
mock_list_1_id = uuid4()

mock_criteria_1_id = uuid4()
mock_subcriteria_1_id = uuid4()

## -------------- mock sections --------------
mock_section_1 = Section(
    section_id=mock_section_1_id,
    name_in_apply_json={"en": "Test Section 1"},
)

## -------------- mock lists --------------
mock_list_1: Lizt = Lizt(
    list_id=mock_list_1_id,
    name="greetings_list",
    type="string",
    items=[{"text": "Hello", "value": "h"}, {"text": "Goodbye", "value": "g"}],
)

## -------------- mock components --------------
mock_component_1_text_field = Component(
    component_id=mock_component_1_id,
    type=ComponentType.TEXT_FIELD,
    title="Organisation name",
    hint_text="This must match your registered legal organisation name",
    page_id=mock_page_1_id,
    page_index=1,
    theme_id=mock_theme_1_id,
    runner_component_name="organisation_name",
)
mock_component_2_email_field = Component(
    component_id=mock_component_2_id,
    type=ComponentType.EMAIL_ADDRESS_FIELD,
    title="What is your email address?",
    hint_text="Work not personal",
    page_id=mock_page_1_id,
    page_index=2,
    theme_id=mock_theme_1_id,
    runner_component_name="email-address",
)
mock_component_3_radio_field: Component = Component(
    component_id=mock_component_3_id,
    page_id=mock_page_2_id,
    title="How is your organisation classified?",
    type=ComponentType.RADIOS_FIELD,
    page_index=1,
    theme_id=mock_theme_1_id,
    theme_index=6,
    options={"hideTitle": False, "classes": ""},
    runner_component_name="organisation_classification",
    list_id=mock_list_1_id,
)
mock_component_4_radio_field_1 = Component(
    component_id=mock_component_4_radio_field_2_id,
    title="org_type",
    type=ComponentType.RADIOS_FIELD,
    runner_component_name="org_type_component",
)
mock_component_4_radio_field_2 = Component(
    component_id=mock_component_4_radio_field_3_id,
    title="org_type",
    type=ComponentType.RADIOS_FIELD,
    runner_component_name="test_c_1",
)
## -------------- mock conditions --------------
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
mock_condition_1 = DbCondition(
    condition_id=mock_condition_1_id,
    name="org_type_c",
    display_name="org type c",
    value=asdict(test_condition_org_type_c.value),
    page_conditions=[
        PageCondition(
            destination_page_path="/org-type-c",
            page_id=mock_page_3_condition_id,
            condition_id=mock_condition_1_id,
        )
    ],
)

mock_condition_2 = DbCondition(
    condition_id=mock_condition_2_id,
    name="org_type_b",
    display_name="org type b",
    value=asdict(test_condition_org_type_b.value),
    page_conditions=[
        PageCondition(
            destination_page_path="/org-type-b",
            page_id=mock_page_3_condition_id,
            condition_id=mock_condition_2_id,
        )
    ],
)
mock_condition_3 = DbCondition(
    condition_id=mock_condition_3_id,
    name="org_type_a",
    display_name="org type a",
    value=asdict(test_condition_org_type_a.value),
    page_conditions=[
        PageCondition(
            destination_page_path="/org-type-a",
            page_id=mock_page_4_condition_id,
            condition_id=mock_condition_3_id,
        )
    ],
)
mock_condition_4 = DbCondition(
    condition_id=mock_condition_4_id,
    name="org_type_b",
    display_name="org type b",
    value=asdict(test_condition_org_type_b.value),
    page_conditions=[
        PageCondition(
            destination_page_path="/org-type-b",
            page_id=mock_page_4_condition_id,
            condition_id=mock_condition_4_id,
        )
    ],
)
mock_condition_5 = DbCondition(
    condition_id=mock_condition_5_id,
    name="org_type_c",
    display_name="org type c",
    value=asdict(test_condition_org_type_c.value),
    page_conditions=[
        PageCondition(
            destination_page_path="/org-type-c",
            page_id=mock_page_4_condition_id,
            condition_id=mock_condition_5_id,
        )
    ],
)
## -------------- mock pages --------------
mock_page_1 = Page(
    page_id=mock_page_1_id,
    name_in_apply_json={"en": "A test page"},
    display_path="test-display-path",
    components=[mock_component_1_text_field, mock_component_2_email_field],
    form_id=mock_form_1_id,
)
mock_page_2 = Page(
    page_id=mock_page_2_id,
    name_in_apply_json={"en": "A test page 2"},
    display_path="test-display-path-2",
    components=[mock_component_3_radio_field],
    form_id=None,
)
test_page_object_org_type_a = Page(
    page_id=test_page_object_org_type_a_id,
    form_id=mock_form_1_id,
    display_path="org-type-a",
    name_in_apply_json={"en": "Organisation Type A"},
    form_index=2,
)
test_page_object_org_type_b = Page(
    page_id=test_page_object_org_type_b_id,
    form_id=mock_form_1_id,
    display_path="org-type-b",
    name_in_apply_json={"en": "Organisation Type B"},
    form_index=2,
)
test_page_object_org_type_c = Page(
    page_id=test_page_object_org_type_c_id,
    form_id=mock_form_1_id,
    display_path="org-type-c",
    name_in_apply_json={"en": "Organisation Type C"},
    form_index=2,
)
mock_page_3_condition = Page(
    page_id=mock_page_3_condition_id,
    form_id=mock_form_1_id,
    display_path="organisation-type",
    name_in_apply_json={"en": "Organisation Type"},
    form_index=1,
    components=[mock_component_4_radio_field_2],
    conditions=[
        mock_condition_1,
        mock_condition_2,
    ],
)
mock_page_4_condition = Page(
    page_id=mock_page_4_condition_id,
    form_id=mock_form_1_id,
    display_path="organisation-type",
    name_in_apply_json={"en": "Organisation Type"},
    form_index=1,
    components=[mock_component_4_radio_field_1],
    conditions=[mock_condition_3, mock_condition_4, mock_condition_5],
)

## -------------- mock forms --------------
mock_form_1 = Form(
    form_id=mock_form_1_id,
    pages=[mock_page_1],
    section_id=mock_section_1_id,
    name_in_apply_json={"en": "A test form"},
    runner_publish_name="a-test-form",
    section_index=1,
)

## -------------- mock assessment --------------
mock_theme_1: Theme = Theme(
    theme_id=mock_theme_1_id,
    subcriteria_id=mock_subcriteria_1_id,
    name="General Information",
    subcriteria_index=1,
    components=[mock_component_1_text_field, mock_component_2_email_field],
)
mock_subcriteria_1: Subcriteria = Subcriteria(
    subcriteria_id=mock_subcriteria_1_id,
    criteria_index=1,
    criteria_id=mock_criteria_1_id,
    name="Organisation Information",
    themes=[mock_theme_1],
)
mock_criteria_1: Criteria = Criteria(
    criteria_id=mock_criteria_1_id, index=1, name="Unscored", weighting=0.0, subcriteria=[mock_subcriteria_1]
)

test_form_json_page_org_type_a = {
    "path": "/org-type-a",
    "title": "org-type-a",
    "components": [],
    "next": [],
    "options": {},
}
test_form_json_page_org_type_b = {
    "path": "/org-type-b",
    "title": "org-type-b",
    "components": [],
    "next": [],
    "options": {},
}
test_form_json_page_org_type_c = {
    "path": "/org-type-c",
    "title": "org-type-c",
    "components": [],
    "next": [],
    "options": {},
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
                "field": {"name": "org_type", "type": "RadiosField", "display": "org type"},
                "operator": "is",
                "value": {"type": "Value", "value": "C2", "display": "C2"},
                "coordinator": "or",
            },
        ],
    },
}
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

mock_fund_id = uuid4()
mock_round_id = uuid4()
mock_section_id = uuid4()
mock_form_id = uuid4()
mock_page_1_id = uuid4()
mock_page_2_id = uuid4()
mock_condition_4_id = uuid4()
mock_condition_5_id = uuid4()
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
        )
    ],
    "pages": [
        Page(
            page_id=mock_page_1_id,
            form_id=mock_form_id,
            display_path="organisation-name",
            name_in_apply_json={"en": "Organisation Name"},
            form_index=1,
        ),
        Page(
            page_id=mock_page_2_id,
            form_id=mock_form_id,
            display_path="organisation-alternative-names",
            name_in_apply_json={"en": "Alternative names of your organisation"},
            form_index=2,
            is_template=True,
        ),
    ],
    "default_next_pages": [
        {"page_id": mock_page_1_id, "default_next_page_id": mock_page_2_id},
    ],
    "components": [
        Component(
            component_id=uuid4(),
            page_id=mock_page_1_id,
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
            page_id=mock_page_1_id,
            title="Does your organisation use any other names?",
            type=ComponentType.YES_NO_FIELD,
            page_index=2,
            theme_id=None,
            options={"hideTitle": False, "classes": ""},
            runner_component_name="does_your_organisation_use_other_names",
            is_template=True,
        ),
        Component(
            component_id=uuid4(),
            page_id=mock_page_2_id,
            title="Alternative Name 1",
            type=ComponentType.TEXT_FIELD,
            page_index=1,
            theme_id=None,
            options={"hideTitle": False, "classes": ""},
            runner_component_name="alt_name_1",
            is_template=True,
        ),
    ],
    "conditions": [
        DbCondition(
            form_id=mock_form_id,
            condition_id=mock_condition_4_id,
            name="organisation_other_names_no",
            display_name="org other names no",
            value=asdict(
                ConditionValue(
                    name="org other names no",
                    conditions=[
                        {
                            "field": {
                                "name": "org_other_names",
                                "type": "YesNoField",
                                "display": "org other names",
                            },
                            "operator": "is",
                            "value": {"type": "Value", "value": "false", "display": "false"},
                            "coordinator": None,
                        },
                    ],
                )
            ),
        ),
        DbCondition(
            form_id=mock_form_id,
            condition_id=mock_condition_5_id,
            name="organisation_other_names_yes",
            display_name="org other names yes",
            value=asdict(
                ConditionValue(
                    name="org other names yes",
                    conditions=[
                        {
                            "field": {
                                "name": "org_other_names",
                                "type": "YesNoField",
                                "display": "org other names",
                            },
                            "operator": "is",
                            "value": {"type": "Value", "value": "true", "display": "false"},
                            "coordinator": None,
                        },
                    ],
                )
            ),
        ),
    ],
    "page_conditions": [
        PageCondition(
            destination_page_path="/summary",
            page_id=mock_page_1_id,
            condition_id=mock_condition_4_id,
        ),
        PageCondition(
            destination_page_path="/organisation-alternative-names",
            page_id=mock_page_1_id,
            condition_id=mock_condition_5_id,
        ),
    ],
}
