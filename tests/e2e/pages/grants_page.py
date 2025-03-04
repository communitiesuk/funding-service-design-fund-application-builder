from playwright.sync_api import Page

from tests.e2e.pages.page_base import PageBase


class GrantsPage(PageBase):
    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url)
        # Initialize locators
        self.add_new_grant = self.page.get_by_role("button", name="Add new grant")

    def when_goto_grants(self):
        """Navigates to the Grants page and waits for it to load."""
        if self.base_url:
            self.page.goto(f"{self.base_url}/grants")
        return self

    def then_click_add_new_grant(self):
        """Clicks the 'Add new grant' button."""
        self.add_new_grant.click()

        from tests.e2e.pages.create_grant_page import CreateGrantPage

        return CreateGrantPage(self.page)
