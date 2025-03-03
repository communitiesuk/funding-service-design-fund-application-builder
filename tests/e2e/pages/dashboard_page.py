from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class DashboardPage(PageBase):
    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url)
        # Initialize locators
        self.add_a_new_grant = self.page.get_by_role("link", name="1. Add a new grant")
        self.setup_a_new_application = self.page.get_by_role("link", name="2. Set up a new application")
        self.design_your_application = self.page.get_by_role("link", name="3. Design your application")
        self.view_and_create_template = self.page.get_by_role("link", name="View and create templates")

    def when_goto_dashboard(self):
        """Navigates to the Dashboard page and waits for it to load."""
        if self.base_url:
            self.page.goto(f"{self.base_url}/dashboard")
            self.page.wait_for_load_state("networkidle")
        return self

    def then_click_add_a_new_grant(self):
        """Clicks the 'Add a new grant' button."""
        self.add_a_new_grant.click()

        from tests.e2e.pages.create_grant_page import CreateGrantPage

        return CreateGrantPage(self.page)

    def and_validate_success_message(self):
        """Validate the success message"""
        banner = self.page.locator(".govuk-notification-banner--success")
        expect(banner.get_by_role("heading", name="New grant added successfully")).to_be_visible()
        expect(banner.locator("a")).to_have_count(2)
        next_step_link = banner.get_by_role("link", name="Set up a new application")
        expect(next_step_link).to_be_visible()
        return self
