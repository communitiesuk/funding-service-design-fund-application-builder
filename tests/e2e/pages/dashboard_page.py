import re

from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class DashboardPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Creating a new grant application")
        self.add_a_new_grant = self.page.get_by_role("link", name="1. Add a new grant")
        self.setup_a_new_application = self.page.get_by_role("link", name="2. Set up a new application")
        self.design_your_application = self.page.get_by_role("link", name="3. Design your application")
        self.view_and_create_template = self.page.get_by_role("link", name="View and create templates")

    def given_user_is_on_dashboard(self):
        """Navigates to the Dashboard page and waits for it to load."""
        if self.base_url:
            self.page.goto(f"{self.base_url}/dashboard")
        return self

    def when_click_add_a_new_grant(self):
        """Clicks the 'Add a new grant' button."""
        self.add_a_new_grant.click()
        from tests.e2e.pages.create_grant_page import CreateGrantPage

        return CreateGrantPage(self.page, metadata=self.metadata)

    def when_click_set_up_a_new_application(self):
        """Clicks the 'Add a new grant' button."""
        self.setup_a_new_application.click()
        from tests.e2e.pages.select_grant_page import SelectGrantPage

        return SelectGrantPage(self.page, metadata=self.metadata)

    def when_click_design_your_application(self):
        """Clicks the 'Add a new grant' button."""
        self.design_your_application.click()
        from tests.e2e.pages.select_grant_page import SelectGrantPage

        return SelectGrantPage(self.page, metadata=self.metadata)

    def then_verify_on_dashboard(self):
        expect(self.title).to_be_visible()
        return self

    def and_validate_template_upload_success_message(self):
        banner = self.page.locator(".govuk-notification-banner--success")
        expect(banner.get_by_role("heading", name="Template uploaded")).to_be_visible()
        expect(banner.locator("a")).to_have_count(1)
        template_name = self.metadata.get("template_name")
        grant_link = self.page.get_by_role("link", name=f"View {template_name}")
        expect(grant_link).to_be_visible()
        self.update_metadata("template_id", re.search(r"[0-9a-fA-F-]{36}$", grant_link.get_attribute("href")).group(0))
        return self

    def and_validate_grant_success_message(self):
        """Validate the grant success message"""
        banner = self.page.locator(".govuk-notification-banner--success")
        expect(banner.get_by_role("heading", name="New grant added successfully")).to_be_visible()
        expect(banner.locator("a")).to_have_count(2)
        grant_name = self.metadata.get("grant_name")
        grant_link = self.page.get_by_role("link", name=f"View {grant_name}")
        expect(grant_link).to_be_visible()
        self.update_metadata("grant_id", re.search(r"[0-9a-fA-F-]{36}$", grant_link.get_attribute("href")).group(0))
        next_step_link = banner.get_by_role("link", name="Set up a new application")
        expect(next_step_link).to_be_visible()
        return self

    def and_validate_application_success_message(self):
        """Validate the application success message"""
        banner = self.page.locator(".govuk-notification-banner--success")
        expect(banner.get_by_role("heading", name="New application created")).to_be_visible()
        expect(banner.locator("a")).to_have_count(2)
        next_step_link = banner.get_by_role("link", name="Design your application")
        expect(next_step_link).to_be_visible()
        return self
