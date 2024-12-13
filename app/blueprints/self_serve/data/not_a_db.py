COMPONENTS = [
    {
        "json_snippet": {
            "options": {"classes": "govuk-input"},
            "type": "TextField",
            "title": "Alternative name 1",
            "schema": {},
        },
        "id": "reuse-alt-org-name-1",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"required": False, "classes": "govuk-input"},
            "type": "TextField",
            "title": "Alternative name 2",
            "schema": {},
        },
        "id": "reuse-alt-org-name-2",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"required": False, "classes": "govuk-input"},
            "type": "TextField",
            "title": "Alternative name 3",
            "schema": {},
        },
        "id": "reuse-alt-org-name-3",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"hideTitle": False, "classes": "govuk-!-width-full"},
            "type": "TextField",
            "title": "Organisation name",
            "hint": "This must match your registered legal organisation name",
            "schema": {},
        },
        "id": "reuse-organisation-name",
        "builder_display_name": "",
    },
    {
        "json_snippet": {"options": {}, "type": "UkAddressField", "title": "Organisation address"},
        "id": "reuse-organisation-address",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"classes": "govuk-!-width-full"},
            "type": "TextField",
            "title": "Which region of England do you work in?",
        },
        "id": "reuse-english-region",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"hideTitle": True, "maxWords": "500"},
            "type": "FreeTextField",
            "title": "What are your organisation's charitable objects?",
            "hint": "You can find this in your organisation's governing document.",
        },
        "id": "reuse-charitable-objects",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"hideTitle": True},
            "type": "RadiosField",
            "title": "Which membership organisations are you a member of?",
            "list": "list_ns_membership_organisations",
        },
        "id": "ns-membership-organisations",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"hideTitle": True, "maxWords": "500"},
            "type": "FreeTextField",
            "title": "What is your organisation's main purpose?",
            "hint": "This is what the organisation was set up to achieve.",
        },
        "id": "reuse-organisation-main-purpose",
        "builder_display_name": "",
    },
    {
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
                "value": "true",  # this must be lowercaes or the navigation doesn't work
                "operator": "is",
                "destination_page": "alternative-organisation-name",
            },
        ],
        "id": "reuse_organisation_other_names_yes_no",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"columnTitles": ["Link", "Action"]},
            "type": "MultiInputField",
            "title": "Website and social media",
            "schema": {},
            "children": [
                {
                    "name": "reuse-web-link",
                    "options": {"classes": "govuk-!-width-full"},
                    "type": "WebsiteField",
                    "title": "Link",
                    "hint": (
                        "<p>For example, your company's Facebook, Instagram or Twitter accounts (if"
                        " applicable)</p><p>You can add more links on the next step</p>"
                    ),
                    "schema": {},
                }
            ],
        },
        "id": "reuse-organisation-website-social-media-links",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"prefix": "\u00a3", "hideTitle": True, "classes": "govuk-input--width-10"},
            "type": "NumberField",
            "title": "Annual turnover for 1 April 2022 to 31 March 2023",
            "hint": '<label class=\\"govuk-body\\" for=\\"YauUjZ\\">1 April 2022 to 31 March 2023</label>',
        },
        "id": "reuse-annual-turnover-23",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"prefix": "\u00a3", "hideTitle": True, "classes": "govuk-input--width-10"},
            "type": "NumberField",
            "hint": '<label class=\\"govuk-body\\" for=\\"zuCRBk\\">1 April 2021 to 31 March 2022</label>',
            "title": "Annual turnover for 1 April 2021 to 31 March 2022",
        },
        "id": "reuse-annual-turnover-22",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"classes": "govuk-!-width-full"},
            "type": "TextField",
            "title": "Name of lead contact",
            "hint": "They will receive all the information about this application.",
        },
        "id": "reuse-lead-contact-name",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"classes": "govuk-!-width-full"},
            "type": "TextField",
            "title": "Lead contact job title",
        },
        "id": "reuse-lead-contact-job-title",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"classes": "govuk-!-width-full"},
            "type": "EmailAddressField",
            "title": "Lead contact email address",
        },
        "id": "reuse-lead-contact-email",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"classes": "govuk-!-width-full"},
            "type": "TelephoneNumberField",
            "title": "Lead contact telephone number",
        },
        "id": "reuse-lead-contact-phone",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {},
            "type": "YesNoField",
            "title": "Is the lead contact the same person as the authorised signatory?",
            "hint": (
                '<p class=\\"govuk-hint\\">An authorised signatory:<ul class=\\"govuk-list govuk-list--bullet'
                ' govuk-hint\\"> <li>is allowed to act on behalf of the organisation</li> <li>will sign the grant'
                " funding agreement if your application is successful</li></ul></p>"
            ),
        },
        "conditions": [
            {
                "name": "lead_contact_same_as_signatory_yes",
                "value": "True",
                "operator": "is",
                "destination_page": "CONTINUE",
            },
            {
                "name": "lead_contact_same_as_signatory_no",
                "value": "False",
                "operator": "is",
                "destination_page": "authorised-signatory-details",
            },
        ],
        "id": "reuse_is_lead_contact_same_as_auth_signatory",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {},
            "type": "Html",
            "content": (
                '<p class=\\"govuk-hint\\">An authorised signatory:</p>\\n<ul class=\\"govuk-list govuk-list--bullet'
                ' govuk-hint\\">\\n            <li>is allowed to act on behalf of the organisation</li>\\n           '
                " <li>will sign the grant funding agreement if your application is successful</li>\\n          </ul>"
            ),
            "schema": {},
            "title": None,
        },
        "id": "auth-sig-intro",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"classes": "govuk-!-width-full"},
            "type": "TextField",
            "title": "Authorised signatory full name",
            "schema": {},
        },
        "id": "auth-sig-full-name",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"required": False, "classes": "govuk-!-width-full"},
            "type": "TextField",
            "title": "Alternative name",
            "schema": {},
        },
        "id": "auth-sig-alt-name",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"required": True, "classes": "govuk-!-width-full"},
            "type": "TextField",
            "title": "Authorised signatory job title",
            "schema": {},
        },
        "id": "auth-sig-job-title",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"classes": "govuk-!-width-full"},
            "type": "EmailAddressField",
            "title": "Authorised signatory email address",
            "schema": {},
        },
        "id": "auth-sig-email",
        "builder_display_name": "",
    },
    {
        "json_snippet": {
            "options": {"classes": "govuk-!-width-full"},
            "type": "TelephoneNumberField",
            "title": "Authorised signatory telephone number",
            "schema": {},
        },
        "id": "auth-sig-phone",
        "builder_display_name": "",
    },
]
PAGES = [
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
        "id": "alternative-organisation-name",
        "form_display_name": "Alternative names of your organisation",
        "builder_display_name": "Alternative organisation names",
        "component_names": ["reuse-alt-org-name-1", "reuse-alt-org-name-2", "reuse-alt-org-name-3"],
        "show_in_builder": False,
    },
    {
        "id": "summary",
        "builder_display_name": "Summary",
        "form_display_name": "Check your answers",
        "component_names": [],
        "show_in_builder": False,
        "controller": "./pages/summary.js",
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
    {
        "id": "ns-org-name",
        "builder_display_name": "NSTF: Organisation Name",
        "form_display_name": "Organisation Name",
        "component_names": [
            "reuse-organisation-name",
            "reuse-organisation-address",
            "reuse-english-region",
        ],
        "show_in_builder": True,
    },
    {
        "id": "organisation-address",
        "builder_display_name": "Organisation Address",
        "form_display_name": "Registered organisation address",
        "component_names": ["reuse-organisation-address"],
        "show_in_builder": True,
    },
    {
        "id": "organisation-main-purpose",
        "builder_display_name": "Organisation Main Purpose",
        "form_display_name": "Organisation Main Purpose",
        "component_names": ["reuse-organisation-main-purpose"],
        "show_in_builder": True,
    },
    {
        "id": "organisation-web-links",
        "builder_display_name": "Organisation Web Links",
        "form_display_name": "Organisation Web Links",
        "component_names": ["reuse-organisation-website-social-media-links"],
        "controller": "RepeatingFieldPageController",
        "show_in_builder": True,
    },
    {
        "id": "annual-turnover",
        "builder_display_name": "Organisation Annual Turnover",
        "form_display_name": "Organisation Annual Turnover",
        "component_names": [
            "reuse-annual-turnover-22",
            "reuse-annual-turnover-23",
        ],
        "show_in_builder": True,
    },
    {
        "id": "ns-membership-organisations",
        "builder_display_name": "NSTF: Membership Organisaions",
        "form_display_name": "Organisation Membership",
        "component_names": ["ns-membership-organisations"],
        "show_in_builder": True,
    },
    {
        "id": "lead-contact-details-and-auth-signatory",
        "builder_display_name": "Lead Contact Details & Auth Signatory",
        "form_display_name": "Lead contact details",
        "component_names": [
            "reuse-lead-contact-name",
            "reuse-lead-contact-job-title",
            "reuse-lead-contact-email",
            "reuse-lead-contact-phone",
            "reuse_is_lead_contact_same_as_auth_signatory",
        ],
        "show_in_builder": True,
    },
    {
        "id": "authorised-signatory-details",
        "form_display_name": "Authorised signatory details",
        "builder_display_name": "Auth Signatory",
        "component_names": [
            "auth-sig-intro",
            "auth-sig-full-name",
            "auth-sig-alt-name",
            "auth-sig-job-title",
            "auth-sig-email",
            "auth-sig-phone",
        ],
        "show_in_builder": False,
    },
]
SECTIONS = []
LISTS = {
    "list_ns_membership_organisations": {
        "type": "string",
        "items": [
            {"text": "Homeless Link", "value": "homeless-link"},
            {"text": "Housing Justice", "value": "housing-justice"},
            {"text": "Both", "value": "both"},
            {"text": "None", "value": "none"},
        ],
    }
}
FORMS = [
    {
        "id": "org-info",
        "builder_display_name": "Organisation Information (Simple)",
        "form_display_name": "Organisation Information",
        "start_page_guidance": "This form will collect information about your organisation",
        "pages": [
            "organisation-single-name",
            "organisation-address",
        ],
    },
]
