from playwright.sync_api import Page

from tests.e2e.dataclass import FabDomains
from tests.e2e.pages.applications_page import ApplicationsPage
from tests.e2e.pages.dashboard_page import DashboardPage


# TC-003-[1]: Add new application from dashboard view
def test_add_new_application_from_dashboard_view(page: Page, domains: FabDomains, user_auth, created_grant):
    (
        DashboardPage(page, domains.fab_url)
        .when_goto_dashboard()
        .then_click_set_up_a_new_application()
        .then_select_a_grant(grant_name=created_grant["grant_name"])
        .then_click_continue()
        .then_fill_application_details()
        .then_click_save_and_return_home()
        .and_validate_application_success_message()
    )


# TC-003-[2]: Add application from applications page
def test_add_application_from_applications_page(page: Page, domains: FabDomains, user_auth, created_grant):
    (
        ApplicationsPage(page, domains.fab_url)
        .when_goto_applications()
        .then_click_create_new_application()
        .then_select_a_grant(grant_name=created_grant["grant_name"])
        .then_click_continue()
        .then_fill_application_details()
        .then_click_save_and_return_home()
        .and_validate_application_success_message()
    )
