from playwright.sync_api import Page

from tests.e2e.dataclass import FabDomains
from tests.e2e.pages.create_grant_page import CreateGrantPage
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.grants_page import GrantsPage


# TC-002-[1]: Add new grant and back to dashboard
def test_add_new_grant_from_dashboard_and_back_to_dashboard(page: Page, domains: FabDomains, user_auth):
    dashboard = DashboardPage(page, domains.fab_url)
    dashboard.when_goto_dashboard()
    dashboard.then_load_components_on_dashboard()
    dashboard.then_click_add_a_new_grant()
    create_grant = CreateGrantPage(page)
    create_grant.then_load_components_on_create_grant_page()
    create_grant.then_fill_non_welsh_competitive_grant_details()
    create_grant.then_click_save_and_return_home()
    dashboard.and_validate_success_message()


# TC-002-[2]: Add new grant from grant page
def test_add_new_grant_from_grants_and_back_to_dashboard(page: Page, domains: FabDomains, user_auth):
    grants = GrantsPage(page, domains.fab_url)
    grants.when_goto_grants()
    grants.then_load_components_on_grants()
    grants.then_click_add_new_grant()
    create_grant = CreateGrantPage(page)
    create_grant.then_load_components_on_create_grant_page()
    create_grant.then_fill_non_welsh_competitive_grant_details()
    create_grant.then_click_save_and_return_home()
    dashboard = DashboardPage(page)
    dashboard.and_validate_success_message()
