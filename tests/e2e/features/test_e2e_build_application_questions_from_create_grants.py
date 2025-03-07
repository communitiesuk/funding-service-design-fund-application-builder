from playwright.sync_api import Page

from tests.e2e.dataclass import FabDomains
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.templates_page import TemplatesPage


# TC-005-[1]: Build application from dashboard view with existing templates in the system
def test_build_application_from_dashboard_view_and_with_existing_templates(page: Page, domains: FabDomains, user_auth):
    (
        DashboardPage(page, domains.fab_url)
        .given_user_is_on_dashboard()
        .then_verify_on_dashboard()
        .when_click_add_a_new_grant()
        .then_verify_on_create_grant()
        .when_fill_non_welsh_competitive_grant_details()
        .when_click_save_and_continue()
        .then_verify_on_create_application()
        .when_fill_application_details()
        .when_click_save_and_continue_and_goto_build_application()
        .then_verify_on_build_application()
        # adding a section 01
        .when_click_add_section()
        .then_verify_on_create_section()
        .when_add_a_section()
        .when_save_and_continue()
        .then_verify_on_build_application()
        # adding a section 02
        .when_click_add_section()
        .then_verify_on_create_section()
        .when_add_a_section()
        .when_save_and_continue()
        .then_verify_on_build_application()
        .when_click_edit_first_section()
        .then_verify_on_edit_section()
        # adding questions to section -1
        .when_adding_some_existing_templates()
        .when_click_add()
        .when_adding_some_existing_templates()
        .when_click_add()
        .when_click_save_and_continue()
        .then_verify_on_build_application()
        .when_click_mark_application_complete()
        .then_verify_application_is_completed()
    )


# TC-005-[2]: Build application from dashboard view with adding new templates
def test_build_application_from_dashboard_view_and_with_adding_templates(page: Page, domains: FabDomains, user_auth):
    (
        TemplatesPage(page, domains.fab_url)
        .given_user_is_on_templates()
        .then_verify_on_templates()
        .when_click_upload_template()
        .then_verify_on_upload_new_template()
        .when_click_upload_file()
        .when_adding_template_details()
        .when_click_save_and_return_home()
        .then_verify_on_dashboard()
        # after template upload, create the grant and application
        .when_click_add_a_new_grant()
        .then_verify_on_create_grant()
        .when_fill_non_welsh_competitive_grant_details()
        .when_click_save_and_continue()
        .then_verify_on_create_application()
        .when_fill_application_details()
        .when_click_save_and_continue_and_goto_build_application()
        .then_verify_on_build_application()
        # adding a section 01
        .when_click_add_section()
        .then_verify_on_create_section()
        .when_add_a_section()
        .when_save_and_continue()
        .then_verify_on_build_application()
        # adding a section 02
        .when_click_add_section()
        .then_verify_on_create_section()
        .when_add_a_section()
        .when_save_and_continue()
        .then_verify_on_build_application()
        .when_click_edit_first_section()
        .then_verify_on_edit_section()
        # adding questions to section -1
        .when_adding_some_existing_templates()
        .when_click_add()
        .when_click_save_and_continue()
        .then_verify_on_build_application()
        .when_click_mark_application_complete()
        .then_verify_application_is_completed()
    )
