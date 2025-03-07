from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class CompleteApplicationPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Application marked as complete")

    def then_verify_application_is_completed(self):
        expect(self.title).to_be_visible()
        return self
