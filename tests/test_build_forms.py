# TODO reinstate this test when finished changing generate_form

# import pytest

# from app.export.config_generator.generate_form import build_form_json

# @pytest.mark.parametrize(
#     "input_json,form_id, form_title, exp_results",
#     [
#         (
#             {
#                 "title": "about-your-organisation",
#                 "pages": ["organisation-name", "organisation-address"],
#             },
#             "form_id_1",
#             "Form Title",
#             {
#                 "startPage": "/intro-about-your-organisation",
#                 "pages": [
#                     {
#                         "path": "/intro-form_id_1",
#                         "title": "Form Title",
#                         "next": [{"path": "/organisation-name"}],
#                     },
#                     {
#                         "path": "/organisation-name",
#                         "title": "Organisation Name",
#                         "next": [
#                             {
#                                 "path": "/organisation-address",
#                                 "condition": "organisation_other_names_no",
#                             },
#                             {
#                                 "path": "/alternative-organisation-name",
#                                 "condition": "organisation_other_names_yes",
#                             },
#                         ],
#                         "exp_component_count": 2,
#                     },
#                     {
#                         "path": "/alternative-organisation-name",
#                         "title": "Alternative names of your organisation",
#                         "next": [
#                             {
#                                 "path": "/organisation-address",
#                             }
#                         ],
#                     },
#                     {
#                         "path": "/organisation-address",
#                         "title": "Registered organisation address",
#                         "next": [{"path": "/summary"}],
#                     },
#                     {
#                         "path": "/summary",
#                         "title": "Check your answers",
#                         "next": [],
#                         "exp_component_count": 0,
#                     },
#                 ],
#             },
#         ),
#         (
#             {
#                 "title": "about-your-organisation",
#                 "pages": [
#                     "organisation-name",
#                     "lead-contact-details-and-auth-signatory",
#                 ],
#             },
#             "abc-123",
#             "This is the name of the form",
#             {
#                 "metadata": {},
#                 "startPage": "/intro-about-your-organisation",
#                 "backLinkText": "Go back to application overview",
#                 "pages": [
#                     {
#                         "path": "/intro-abc-123",
#                         "title": "This is the name of the form",
#                         "components": [],
#                         "next": [{"path": "/organisation-name"}],
#                         "options": {},
#                         "controller": "./pages/start.js",
#                     },
#                     {
#                         "path": "/organisation-name",
#                         "title": "Organisation Name",
#                         "components": [
#                             {
#                                 "options": {
#                                     "hideTitle": False,
#                                     "classes": "govuk-!-width-full",
#                                 },
#                                 "type": "TextField",
#                                 "title": "Organisation name",
#                                 "hint": "This must match your registered legal organisation name",
#                                 "schema": {},
#                                 "name": "reuse-organisation-name",
#                             },
#                             {
#                                 "options": {},
#                                 "type": "YesNoField",
#                                 "title": "Does your organisation use any other names?",
#                                 "schema": {},
#                                 "name": "reuse_organisation_other_names_yes_no",
#                             },
#                         ],
#                         "next": [
#                             {
#                                 "path": "/lead-contact-details-and-auth-signatory",
#                                 "condition": "organisation_other_names_no",
#                             },
#                             {
#                                 "path": "/alternative-organisation-name",
#                                 "condition": "organisation_other_names_yes",
#                             },
#                         ],
#                         "options": {},
#                     },
#                     {
#                         "path": "/lead-contact-details-and-auth-signatory",
#                         "title": "Lead contact details",
#                         "components": [
#                             {
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TextField",
#                                 "title": "Name of lead contact",
#                                 "hint": "They will receive all the information about this application.",
#                                 "name": "reuse-lead-contact-name",
#                             },
#                             {
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TextField",
#                                 "title": "Lead contact job title",
#                                 "name": "reuse-lead-contact-job-title",
#                             },
#                             {
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "EmailAddressField",
#                                 "title": "Lead contact email address",
#                                 "name": "reuse-lead-contact-email",
#                             },
#                             {
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TelephoneNumberField",
#                                 "title": "Lead contact telephone number",
#                                 "name": "reuse-lead-contact-phone",
#                             },
#                             {
#                                 "options": {},
#                                 "type": "YesNoField",
#                                 "title": "Is the lead contact the same person as the authorised signatory?",
#                                 "hint": "<p class='govuk-hint'>An authorised signatory:"
#                                 "<ul class='govuk-list govuk-list--bullet govuk-hint'>
# <li>is allowed to act on behalf"
#                                 " of the organisation</li> "
#                                 "<li>will sign the grant funding agreement if your application is "
#                                 "successful</li></ul></p>",
#                                 "name": "reuse_is_lead_contact_same_as_auth_signatory",
#                             },
#                         ],
#                         "next": [
#                             {
#                                 "path": "/summary",
#                                 "condition": "lead_contact_same_as_signatory_yes",
#                             },
#                             {
#                                 "path": "/authorised-signatory-details",
#                                 "condition": "lead_contact_same_as_signatory_no",
#                             },
#                         ],
#                         "options": {},
#                     },
#                     {
#                         "path": "/alternative-organisation-name",
#                         "title": "Alternative names of your organisation",
#                         "components": [
#                             {
#                                 "name": "reuse-alt-org-name-1",
#                                 "options": {"classes": "govuk-input"},
#                                 "type": "TextField",
#                                 "title": "Alternative name 1",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "reuse-alt-org-name-2",
#                                 "options": {
#                                     "required": False,
#                                     "classes": "govuk-input",
#                                 },
#                                 "type": "TextField",
#                                 "title": "Alternative name 2",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "reuse-alt-org-name-3",
#                                 "options": {
#                                     "required": False,
#                                     "classes": "govuk-input",
#                                 },
#                                 "type": "TextField",
#                                 "title": "Alternative name 3",
#                                 "schema": {},
#                             },
#                         ],
#                         "next": [{"path": "/lead-contact-details-and-auth-signatory"}],
#                     },
#                     {
#                         "path": "/authorised-signatory-details",
#                         "title": "Authorised signatory details",
#                         "components": [
#                             {
#                                 "name": "xKWJWW",
#                                 "options": {},
#                                 "type": "Html",
#                                 "content": "<p class='govuk-hint'>An authorised signatory:</p>\\n"
#                                 "<ul class='govuk-list govuk-list--bullet govuk-hint'>\\n
# <li>is allowed to"
#                                 " act on behalf of the organisation</li>\\n            <li>will sign the grant "
#                                 "funding agreement if your application is successful</li>\\n          </ul>",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "pDrPDz",
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TextField",
#                                 "title": "Authorised signatory full name",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "teowxM",
#                                 "options": {
#                                     "required": False,
#                                     "classes": "govuk-!-width-full",
#                                 },
#                                 "type": "TextField",
#                                 "title": "Alternative name",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "tikwxM",
#                                 "options": {
#                                     "required": True,
#                                     "classes": "govuk-!-width-full",
#                                 },
#                                 "type": "TextField",
#                                 "title": "Authorised signatory job title",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "ljfzCy",
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "EmailAddressField",
#                                 "title": "Authorised signatory email address",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "gNgJme",
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TelephoneNumberField",
#                                 "title": "Authorised signatory telephone number",
#                                 "schema": {},
#                             },
#                         ],
#                         "next": [{"path": "/summary"}],
#                     },
#                     {
#                         "path": "/summary",
#                         "title": "Check your answers",
#                         "components": [],
#                         "next": [],
#                         "section": "uLwBuz",
#                         "controller": "./pages/summary.js",
#                     },
#                 ],
#                 "lists": [],
#                 "conditions": [
#                     {
#                         "displayName": "organisation_other_names_no",
#                         "name": "organisation_other_names_no",
#                         "value": {
#                             "name": "organisation_other_names_no",
#                             "conditions": [
#                                 {
#                                     "field": {
#                                         "name": "reuse_organisation_other_names_yes_no",
#                                         "type": "YesNoField",
#                                         "display": "Does your organisation use any other names?",
#                                     },
#                                     "operator": "is",
#                                     "value": {
#                                         "type": "Value",
#                                         "value": "False",
#                                         "display": "False",
#                                     },
#                                 }
#                             ],
#                         },
#                     },
#                     {
#                         "displayName": "organisation_other_names_yes",
#                         "name": "organisation_other_names_yes",
#                         "value": {
#                             "name": "organisation_other_names_yes",
#                             "conditions": [
#                                 {
#                                     "field": {
#                                         "name": "reuse_organisation_other_names_yes_no",
#                                         "type": "YesNoField",
#                                         "display": "Does your organisation use any other names?",
#                                     },
#                                     "operator": "is",
#                                     "value": {
#                                         "type": "Value",
#                                         "value": "True",
#                                         "display": "True",
#                                     },
#                                 }
#                             ],
#                         },
#                     },
#                     {
#                         "displayName": "lead_contact_same_as_signatory_yes",
#                         "name": "lead_contact_same_as_signatory_yes",
#                         "value": {
#                             "name": "lead_contact_same_as_signatory_yes",
#                             "conditions": [
#                                 {
#                                     "field": {
#                                         "name": "reuse_is_lead_contact_same_as_auth_signatory",
#                                         "type": "YesNoField",
#                                         "display": "Is the lead contact the same person as the authorised signatory?",
#                                     },
#                                     "operator": "is",
#                                     "value": {
#                                         "type": "Value",
#                                         "value": "True",
#                                         "display": "True",
#                                     },
#                                 }
#                             ],
#                         },
#                     },
#                     {
#                         "displayName": "lead_contact_same_as_signatory_no",
#                         "name": "lead_contact_same_as_signatory_no",
#                         "value": {
#                             "name": "lead_contact_same_as_signatory_no",
#                             "conditions": [
#                                 {
#                                     "field": {
#                                         "name": "reuse_is_lead_contact_same_as_auth_signatory",
#                                         "type": "YesNoField",
#                                         "display": "Is the lead contact the same person as the authorised signatory?",
#                                     },
#                                     "operator": "is",
#                                     "value": {
#                                         "type": "Value",
#                                         "value": "False",
#                                         "display": "False",
#                                     },
#                                 }
#                             ],
#                         },
#                     },
#                 ],
#                 "fees": [],
#                 "sections": [],
#                 "outputs": [
#                     {
#                         "name": "update-form",
#                         "title": "Update form in application store",
#                         "type": "savePerPage",
#                         "outputConfiguration": {
#                             "savePerPageUrl": "https://webhook.site/a8d808ca-bf5e-4aea-aebc-f3d9bc93a435"
#                         },
#                     }
#                 ],
#                 "skipSummary": False,
#                 "name": "Generated by question bank 2024-06-18 13:54:24.954418",
#             },
#         ),
#         (
#             {
#                 "title": "about-your-organisation",
#                 "pages": [
#                     "lead-contact-details-and-auth-signatory",
#                 ],
#             },
#             "abc-123",
#             "This is the name of the form",
#             {
#                 "metadata": {},
#                 "startPage": "/intro-about-your-organisation",
#                 "backLinkText": "Go back to application overview",
#                 "pages": [
#                     {
#                         "path": "/intro-abc-123",
#                         "title": "This is the name of the form",
#                         "components": [],
#                         "next": [{"path": "/lead-contact-details-and-auth-signatory"}],
#                         "options": {},
#                         "controller": "./pages/start.js",
#                     },
#                     {
#                         "path": "/lead-contact-details-and-auth-signatory",
#                         "title": "Lead contact details",
#                         "components": [
#                             {
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TextField",
#                                 "title": "Name of lead contact",
#                                 "hint": "They will receive all the information about this application.",
#                                 "name": "reuse-lead-contact-name",
#                             },
#                             {
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TextField",
#                                 "title": "Lead contact job title",
#                                 "name": "reuse-lead-contact-job-title",
#                             },
#                             {
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "EmailAddressField",
#                                 "title": "Lead contact email address",
#                                 "name": "reuse-lead-contact-email",
#                             },
#                             {
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TelephoneNumberField",
#                                 "title": "Lead contact telephone number",
#                                 "name": "reuse-lead-contact-phone",
#                             },
#                             {
#                                 "options": {},
#                                 "type": "YesNoField",
#                                 "title": "Is the lead contact the same person as the authorised signatory?",
#                                 "hint": "<p class='govuk-hint'>An authorised signatory:<ul class='govuk-list"
#                                 " govuk-list--bullet govuk-hint'> <li>is allowed to act on behalf of the "
#                                 "organisation</li> <li>will sign the grant funding agreement if your "
#                                 "application is successful</li></ul></p>",
#                                 "name": "reuse_is_lead_contact_same_as_auth_signatory",
#                             },
#                         ],
#                         "next": [
#                             {
#                                 "path": "/summary",
#                                 "condition": "lead_contact_same_as_signatory_yes",
#                             },
#                             {
#                                 "path": "/authorised-signatory-details",
#                                 "condition": "lead_contact_same_as_signatory_no",
#                             },
#                         ],
#                         "options": {},
#                     },
#                     {
#                         "path": "/authorised-signatory-details",
#                         "title": "Authorised signatory details",
#                         "components": [
#                             {
#                                 "name": "xKWJWW",
#                                 "options": {},
#                                 "type": "Html",
#                                 "content": "<p class='govuk-hint'>An authorised signatory:</p>\\n
# <ul class='govuk-list"
#                                 " govuk-list--bullet govuk-hint'>\\n            <li>is allowed to act on behalf of "
#                                 "the organisation</li>\\n            <li>will sign the grant funding agreement if "
#                                 "your application is successful</li>\\n          </ul>",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "pDrPDz",
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TextField",
#                                 "title": "Authorised signatory full name",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "teowxM",
#                                 "options": {
#                                     "required": False,
#                                     "classes": "govuk-!-width-full",
#                                 },
#                                 "type": "TextField",
#                                 "title": "Alternative name",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "tikwxM",
#                                 "options": {
#                                     "required": True,
#                                     "classes": "govuk-!-width-full",
#                                 },
#                                 "type": "TextField",
#                                 "title": "Authorised signatory job title",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "ljfzCy",
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "EmailAddressField",
#                                 "title": "Authorised signatory email address",
#                                 "schema": {},
#                             },
#                             {
#                                 "name": "gNgJme",
#                                 "options": {"classes": "govuk-!-width-full"},
#                                 "type": "TelephoneNumberField",
#                                 "title": "Authorised signatory telephone number",
#                                 "schema": {},
#                             },
#                         ],
#                         "next": [{"path": "/summary"}],
#                     },
#                     {
#                         "path": "/summary",
#                         "title": "Check your answers",
#                         "components": [],
#                         "next": [],
#                         "section": "uLwBuz",
#                         "controller": "./pages/summary.js",
#                     },
#                 ],
#                 "lists": [],
#                 "conditions": [
#                     {
#                         "displayName": "lead_contact_same_as_signatory_yes",
#                         "name": "lead_contact_same_as_signatory_yes",
#                         "value": {
#                             "name": "lead_contact_same_as_signatory_yes",
#                             "conditions": [
#                                 {
#                                     "field": {
#                                         "name": "reuse_is_lead_contact_same_as_auth_signatory",
#                                         "type": "YesNoField",
#                                         "display": "Is the lead contact the same person as the authorised signatory?",
#                                     },
#                                     "operator": "is",
#                                     "value": {
#                                         "type": "Value",
#                                         "value": "True",
#                                         "display": "True",
#                                     },
#                                 }
#                             ],
#                         },
#                     },
#                     {
#                         "displayName": "lead_contact_same_as_signatory_no",
#                         "name": "lead_contact_same_as_signatory_no",
#                         "value": {
#                             "name": "lead_contact_same_as_signatory_no",
#                             "conditions": [
#                                 {
#                                     "field": {
#                                         "name": "reuse_is_lead_contact_same_as_auth_signatory",
#                                         "type": "YesNoField",
#                                         "display": "Is the lead contact the same person as the authorised signatory?",
#                                     },
#                                     "operator": "is",
#                                     "value": {
#                                         "type": "Value",
#                                         "value": "False",
#                                         "display": "False",
#                                     },
#                                 }
#                             ],
#                         },
#                     },
#                 ],
#                 "fees": [],
#                 "sections": [],
#                 "outputs": [
#                     {
#                         "name": "update-form",
#                         "title": "Update form in application store",
#                         "type": "savePerPage",
#                         "outputConfiguration": {
#                             "savePerPageUrl": "https://webhook.site/a8d808ca-bf5e-4aea-aebc-f3d9bc93a435"
#                         },
#                     }
#                 ],
#                 "skipSummary": False,
#                 "name": "Generated by question bank 2024-06-18 13:54:24.954418",
#             },
#         ),
#     ],
# )
# def test_build_form(input_form, exp_results):
#     results = build_form_json(form=input_form)
#     assert results
#     assert len(results["pages"]) == len(exp_results["pages"])
#     assert results["name"] == input_form.name_in_apply_json["en"]
#     for exp_page in exp_results["pages"]:
#         result_page = next(res_page for res_page in results["pages"] if res_page["path"] == exp_page["path"])
#         assert result_page["title"] == exp_page["title"]
#         if "exp_component_count" in exp_page:
#             assert len(result_page["components"]) == exp_page["exp_component_count"]
#         if "next" in exp_page:
#             for exp_next in exp_page["next"]:
#                 assert exp_next["path"] in [next["path"] for next in result_page["next"]]
#                 if "condition" in exp_next:
#                     assert exp_next["condition"] in [next["condition"] for next in result_page["next"]]
