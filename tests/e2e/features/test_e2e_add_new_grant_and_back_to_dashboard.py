from playwright.sync_api import Page

from tests.e2e.dataclass import FabDomains
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.grants_page import GrantsPage


# TC-002-[1]: Add new grant and back to dashboard
def test_add_new_grant_from_dashboard_and_back_to_dashboard(page: Page, domains: FabDomains, user_auth):
    (
        DashboardPage(page, domains.fab_url)
        .when_goto_dashboard()
        .then_click_add_a_new_grant()
        .then_fill_non_welsh_competitive_grant_details()
        .then_click_save_and_return_home()
        .and_validate_grant_success_message()
    )


# TC-002-[2]: Add new grant from grant page
def test_add_new_grant_from_grants_and_back_to_dashboard(page: Page, domains: FabDomains, user_auth):
    (
        GrantsPage(page, domains.fab_url)
        .when_goto_grants()
        .then_click_add_new_grant()
        .then_fill_non_welsh_competitive_grant_details()
        .then_click_save_and_return_home()
        .and_validate_grant_success_message()
    )
