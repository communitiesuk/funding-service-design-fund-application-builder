from playwright.sync_api import Locator, Page

from tests.e2e.pages.page_base import PageBase


class GrantsPage(PageBase):
    add_new_grant: Locator

    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url)

    def when_goto_grants(self):
        if self.base_url:
            self.page.goto(f"{self.base_url}/grants")

    def then_load_grants(self):
        self.add_new_grant = self.page.get_by_role("button", name="Add new grant")

    def then_click_add_new_grant(self):
        self.add_new_grant.click()
