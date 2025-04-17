from playwright.sync_api import Locator, Page, expect

from tests.e2e.pages.build_application_page import BuildApplicationPage
from tests.e2e.pages.page_base import PageBase


class SelectApplicationPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.select_application: Locator = self.page.get_by_role("combobox", name="Select or create an application")
        self.continue_btn: Locator = self.page.get_by_role("button", name="Continue")

    def when_select_an_application(self, round_id: str = None):
        self.select_application.wait_for(state="visible")
        round_id = round_id or self.metadata.get("round_id")
        available_round_ids = [
            opt.get_attribute("value") for opt in self.select_application.locator("option").all()[1:]
        ]
        if not round_id or round_id not in available_round_ids:
            raise ValueError(f"Round ID '{round_id}' not found in available round IDs: {available_round_ids}")
        self.select_application.select_option(value=round_id)
        return self

    def when_click_continue(self):
        self.continue_btn.click()
        return self

    def then_verify_on_select_application(self):
        expect(self.select_application).to_be_visible()
        return self

    def then_expect_build_application(self):
        return BuildApplicationPage(self.page, metadata=self.metadata)
