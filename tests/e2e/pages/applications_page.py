from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class ApplicationsPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url, metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Applications")
        self.create_new_application = self.page.get_by_role("button", name="Create new application")

    def given_goto_applications(self):
        if self.base_url:
            self.page.goto(f"{self.base_url}/rounds")
        return self

    def when_click_create_new_application(self):
        self.create_new_application.click()
        from tests.e2e.pages.select_grant_page import SelectGrantPage

        return SelectGrantPage(self.page, self.metadata)

    def then_verify_on_applications(self):
        expect(self.title).to_be_visible()
        return self

    def and_validate_application_success_message(self):
        banner = self.page.locator(".govuk-notification-banner--success")
        expect(banner.get_by_role("heading", name="New application created")).to_be_visible()
        expect(banner.locator("a")).to_have_count(1)
        return self
