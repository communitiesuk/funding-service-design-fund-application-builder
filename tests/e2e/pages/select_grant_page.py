import random

from playwright.sync_api import Locator, Page, expect

from tests.e2e.pages.create_application_page import CreateApplicationPage
from tests.e2e.pages.page_base import PageBase


class SelectGrantPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.select_grant: Locator = self.page.get_by_role("combobox", name="Select or add a grant")
        self.continue_btn: Locator = self.page.get_by_role("button", name="Continue")

    def when_select_a_grant(self, grant_name: str = None):
        """Select a grant from the dropdown."""
        self.select_grant.wait_for(state="visible")
        grant_options = [
            {"label": option.text_content(), "value": option.get_attribute("value")}
            for option in self.select_grant.locator("option").all()[1:]
        ]
        if grant_name is None:
            selected_grant = random.choice(grant_options)
        else:
            matching_grants = [
                option
                for option in grant_options
                if grant_name.lower() in option["label"].lower() or grant_name.lower() in option["value"].lower()
            ]
            if not matching_grants:
                raise ValueError(f"Error: Grant '{grant_name}' not found. No matching grants available.")
            selected_grant = matching_grants[0]
        self.select_grant.select_option(value=selected_grant["value"])
        return self

    def when_click_continue(self):
        self.continue_btn.click()
        return CreateApplicationPage(self.page, base_url=self.base_url, metadata=self.metadata)

    def then_verify_on_select_grant(self):
        expect(self.select_grant).to_be_visible()
        return self
