from playwright.sync_api import Page

from tests.e2e.dataclass import FabDomains
from tests.e2e.pages.applications_page import ApplicationsPage
from tests.e2e.pages.dashboard_page import DashboardPage


# TC-003-[1]: Add new application from dashboard view
def test_add_new_application_from_dashboard_view(page: Page, domains: FabDomains, user_auth, created_grant):
    (
        DashboardPage(page, domains.fab_url)
        .given_user_is_on_dashboard()
        .then_verify_on_dashboard()
        .when_click_set_up_a_new_application()
        .then_verify_on_select_grant()
        .when_select_a_grant(grant_name=created_grant["grant_name"])
        .when_click_continue()
        .then_verify_on_create_application()
        .when_fill_application_details()
        .when_click_save_and_return_home()
        .then_verify_on_dashboard()
        .and_validate_application_success_message()
    )


# TC-003-[2]: Add application from applications page and comeback dashboard
def test_add_application_from_applications_page_and_goback_dashboard(
    page: Page, domains: FabDomains, user_auth, created_grant
):
    (
        ApplicationsPage(page, domains.fab_url)
        .when_goto_applications()
        .then_verify_on_application()
        .when_click_create_new_application()
        .then_verify_on_select_grant()
        .when_select_a_grant(grant_name=created_grant["grant_name"])
        .when_click_continue()
        .then_verify_on_create_application()
        .when_fill_application_details()
        .when_click_save_and_return_home()
        .then_verify_on_dashboard()
        .and_validate_application_success_message()
    )


# TC-003-[3]: Add application from applications page and comeback applications page
def test_add_application_from_applications_page_and_goback_application_page(
    page: Page, domains: FabDomains, user_auth, created_grant
):
    (
        ApplicationsPage(page, domains.fab_url)
        .when_goto_applications()
        .then_verify_on_application()
        .when_click_create_new_application()
        .then_verify_on_select_grant()
        .when_select_a_grant(grant_name=created_grant["grant_name"])
        .when_click_continue()
        .then_verify_on_create_application()
        .when_fill_application_details()
        .when_click_save_and_continue()
        .then_verify_on_application()
        .and_validate_application_success_message()
    )
