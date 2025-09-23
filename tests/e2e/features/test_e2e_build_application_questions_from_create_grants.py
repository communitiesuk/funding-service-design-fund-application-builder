from playwright.sync_api import Page

from tests.e2e.dataclass import FabDomains
from tests.e2e.pages.dashboard_page import DashboardPage


# TC-005: Build application from dashboard view with adding new templates
def test_e2e_grant_creation_to_application_completion_flow(page: Page, domains: FabDomains, user_auth):
    output = None
    try:
        output = (
            DashboardPage(page, domains.fab_url)
            .given_user_is_on_dashboard()
            .when_click_add_a_new_grant()
            .then_verify_on_create_grant()
            .when_fill_non_welsh_competitive_grant_details()
            .when_click_save_and_continue()
            # create application
            .then_verify_on_create_application()
            .and_validate_grant_success_message()
            .when_fill_application_details()
            .when_click_save_and_continue()
            .then_expect_build_application()
            .and_verify_on_build_application()
            .and_validate_application_success_message()
            # build application and adding a section 01
            .when_click_add_section()
            .then_verify_on_create_section()
            .when_fill_section_details()
            .when_save_and_continue()
            .then_verify_on_build_application()
            .and_validate_section_added_success_message()
            .and_validate_sections_are_available()
            # adding a section 02
            .when_click_add_section()
            .then_verify_on_create_section()
            .when_fill_section_details()
            .when_save_and_continue()
            .then_verify_on_build_application()
            .and_validate_section_added_success_message()
            .and_validate_sections_are_available()
            # edit section 01
            .when_click_edit_first_section()
            .then_verify_on_edit_section()
            # adding questions to section -1
            .when_add_template()
            .when_click_add()
            .when_click_save_and_continue()
            .then_verify_on_build_application()
            .and_validate_section_updated_success_message()
            .when_click_down_on_section()
            .then_verify_section_gone_down()
            .when_click_up_on_section()
            .then_verify_section_gone_up()
            # mark application complete
            .when_click_mark_application_complete()
            .then_verify_on_application_complete()
            .when_click_download()
            .then_validate_download_success()
        )
    finally:
        if domains.environment != "e2e":
            if grant_id := output.metadata.get("grant_id"):
                page.request.fetch(f"{domains.fab_url}/grants/{grant_id}", method="DELETE")
            if template_id := output.metadata.get("template_id"):
                page.request.fetch(f"{domains.fab_url}/templates/{template_id}", method="DELETE")
