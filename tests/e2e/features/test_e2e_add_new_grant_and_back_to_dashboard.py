from playwright.sync_api import Page

from tests.e2e.dataclass import FabDomains
from tests.e2e.http_client import HttpClient
from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.grants_page import GrantsPage


# TC-002-[1]: Add new grant and back to dashboard
def test_add_new_grant_from_dashboard_and_back_to_dashboard(page: Page, domains: FabDomains, user_auth):
    output = None
    try:
        output = (
            DashboardPage(page, domains.fab_url)
            .given_user_is_on_dashboard()
            .then_verify_on_dashboard()
            .when_click_add_a_new_grant()
            .then_verify_on_create_grant()
            .when_fill_non_welsh_competitive_grant_details()
            .when_click_save_and_return_home()
            .then_verify_on_dashboard()
            .and_validate_grant_success_message()
        )
    finally:
        if domains.environment != "e2e":
            HttpClient(base_url=domains.fab_url).delete(output, "grants")


# TC-002-[2]: Add new grant from grant page
def test_add_new_grant_from_grants_and_back_to_dashboard(page: Page, domains: FabDomains, user_auth):
    output = None
    try:
        output = (
            GrantsPage(page, domains.fab_url)
            .given_user_is_on_grants()
            .then_verify_on_grants()
            .when_click_add_new_grant()
            .then_verify_on_create_grant()
            .when_fill_non_welsh_competitive_grant_details()
            .when_click_save_and_return_home()
            .then_verify_on_dashboard()
            .and_validate_grant_success_message()
        )
    finally:
        if domains.environment != "e2e":
            HttpClient(base_url=domains.fab_url).delete(output, "grants")
