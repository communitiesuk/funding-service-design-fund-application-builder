from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class ApplicationsPage(PageBase):
    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Applications")
        self.create_new_application = self.page.get_by_role("button", name="Create new application")

    def when_goto_applications(self):
        if self.base_url:
            self.page.goto(f"{self.base_url}/rounds")
        return self

    def when_click_create_new_application(self):
        self.create_new_application.click()
        from tests.e2e.pages.select_grant_page import SelectGrantPage

        return SelectGrantPage(self.page)

    def then_verify_on_application(self):
        expect(self.title).to_be_visible()
        return self
