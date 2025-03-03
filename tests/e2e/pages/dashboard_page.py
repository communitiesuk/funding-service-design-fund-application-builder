from playwright.sync_api import Locator, Page, expect

from tests.e2e.pages.page_base import PageBase


class DashboardPage(PageBase):
    add_a_new_grant: Locator
    setup_a_new_application: Locator
    design_your_application: Locator
    view_and_create_template: Locator

    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url)

    def when_goto_dashboard(self):
        if self.base_url:
            self.page.goto(f"{self.base_url}/dashboard")

    def then_load_components_on_dashboard(self):
        self.add_a_new_grant = self.page.get_by_role("link", name="1. Add a new grant")
        self.setup_a_new_application = self.page.get_by_role("link", name="2. Set up a new application")
        self.design_your_application = self.page.get_by_role("link", name="3. Design your application")
        self.view_and_create_template = self.page.get_by_role("link", name="View and create templates")

    def then_click_add_a_new_grant(self):
        self.add_a_new_grant.click()

    def then_click_setup_a_new_application(self):
        self.setup_a_new_application.click()

    def then_click_design_your_application(self):
        self.design_your_application.click()

    def then_click_view_and_create_template(self):
        self.view_and_create_template.click()

    def and_validate_success_message(self):
        banner = self.page.locator(".govuk-notification-banner--success")
        expect(banner.get_by_role("heading", name="New grant added successfully")).to_be_visible()
        expect(banner.locator("a")).to_have_count(2)
        next_step_link = banner.get_by_role("link", name="Set up a new application")
        expect(next_step_link).to_be_visible()
