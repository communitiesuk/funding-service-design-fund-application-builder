from playwright.sync_api import Page

from tests.e2e.dataclass import FabDomains
from tests.e2e.pages.applications_page import ApplicationsPage
from tests.e2e.pages.dashboard_page import DashboardPage


# TC-003-[1]: Add new application from dashboard view
def test_add_application_from_dashboard_view(page: Page, domains: FabDomains, user_auth, created_grant):
    try:
        (
            DashboardPage(page, domains.fab_url)
            .given_user_is_on_dashboard()
            .then_verify_on_dashboard()
            .when_click_set_up_a_new_application()
            .then_verify_on_select_grant()
            .when_select_a_grant(grant_name=created_grant.metadata.get("grant_name"))
            .when_click_continue()
            .then_expect_create_application()
            .and_verify_on_create_application()
            .and_verify_grant_on_create_application(grant_name=created_grant.metadata.get("grant_name"))
            .when_fill_application_details()
            .when_click_save_and_return_home()
            .then_verify_on_dashboard()
            .and_validate_application_success_message()
        )
    finally:
        grant_id = created_grant.metadata.get("grant_id")
        if grant_id and domains.environment != "e2e":
            page.request.fetch(f"{domains.fab_url}/grants/{grant_id}", method="DELETE")


# TC-003-[2]: Add application from applications page and comeback dashboard
def test_add_application_from_applications_page_and_goback_dashboard(
    page: Page, domains: FabDomains, user_auth, created_grant
):
    try:
        (
            ApplicationsPage(page, domains.fab_url)
            .given_goto_applications()
            .then_verify_on_applications()
            .when_click_create_new_application()
            .then_verify_on_select_grant()
            .when_select_a_grant(grant_name=created_grant.metadata.get("grant_name"))
            .when_click_continue()
            .then_expect_create_application()
            .and_verify_on_create_application()
            .when_fill_application_details()
            .when_click_save_and_return_home()
            .then_verify_on_dashboard()
            .and_validate_application_success_message()
        )
    finally:
        grant_id = created_grant.metadata.get("grant_id")
        if grant_id and domains.environment != "e2e":
            page.request.fetch(f"{domains.fab_url}/grants/{grant_id}", method="DELETE")


# TC-003-[3]: Add application from applications page and comeback applications page
def test_add_application_from_applications_page_and_goback_application_page(
    page: Page, domains: FabDomains, user_auth, created_grant
):
    try:
        (
            ApplicationsPage(page, domains.fab_url)
            .given_goto_applications()
            .then_verify_on_applications()
            .when_click_create_new_application()
            .then_verify_on_select_grant()
            .when_select_a_grant(grant_name=created_grant.metadata.get("grant_name"))
            .when_click_continue()
            .then_expect_create_application()
            .and_verify_on_create_application()
            .when_fill_application_details()
            .when_click_save_and_continue()
            .then_expect_applications()
            .and_verify_on_applications()
            .and_validate_application_success_message()
        )
    finally:
        grant_id = created_grant.metadata.get("grant_id")
        if grant_id and domains.environment != "e2e":
            page.request.fetch(f"{domains.fab_url}/grants/{grant_id}", method="DELETE")
