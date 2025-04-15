from playwright.sync_api import Locator, Page, expect

from tests.e2e.pages.page_base import PageBase


class SelectGrantPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.select_grant: Locator = self.page.get_by_role("combobox", name="Select or add a grant")
        self.continue_btn: Locator = self.page.get_by_role("button", name="Continue")

    def when_select_a_grant(self, grant_id: str = None):
        """Select a grant from the dropdown."""
        self.select_grant.wait_for(state="visible")
        grant_id = grant_id or self.metadata.get("grant_id")
        available_grant_ids = [opt.get_attribute("value") for opt in self.select_grant.locator("option").all()[1:]]
        if not grant_id or grant_id not in available_grant_ids:
            raise ValueError(f"Grant ID '{grant_id}' not found in available grant IDs: {available_grant_ids}")
        self.select_grant.select_option(value=grant_id)
        return self

    def when_click_continue(self):
        self.continue_btn.click()
        return self

    def then_expect_create_application(self):
        from tests.e2e.pages.create_application_page import CreateApplicationPage

        return CreateApplicationPage(self.page, metadata=self.metadata)

    def then_expect_select_application(self):
        from tests.e2e.pages.select_application_page import SelectApplicationPage

        return SelectApplicationPage(self.page, metadata=self.metadata)

    def then_verify_on_select_grant(self):
        expect(self.select_grant).to_be_visible()
        return self
