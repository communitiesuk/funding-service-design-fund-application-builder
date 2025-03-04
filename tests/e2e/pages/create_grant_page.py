from typing import Literal

from playwright.sync_api import Locator, Page

from tests.e2e.pages.page_base import PageBase


class CreateGrantPage(PageBase):
    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url)
        # Initialize locators
        self.is_welsh: Locator = self.page.get_by_role("group", name="Is this grant available in Welsh?")
        self.grant_name: Locator = self.page.get_by_role("textbox", name="Grant name", exact=True)
        self.grant_short_name: Locator = self.page.get_by_role("textbox", name="Grant short name", exact=True)
        self.application_name: Locator = self.page.get_by_role("textbox", name="Application name", exact=True)
        self.grant_description: Locator = self.page.get_by_role("textbox", name="Grant description", exact=True)
        self.grant_type: Locator = self.page.get_by_role("group", name="Funding type")
        self.ggis_field: Locator = self.page.get_by_role("textbox", name="GGIS scheme reference number")

        self.save_and_continue: Locator = self.page.get_by_role("button", name="Save and continue")
        self.cancel: Locator = self.page.get_by_role("link", name="Cancel")
        self.save_and_return_home: Locator = self.page.get_by_role("button", name="Save and return home")

    def go_to_create_grant_page(self):
        """Navigates to the Create Grant page and waits for it to load."""
        if self.base_url:
            self.page.goto(f"{self.base_url}/grants/create")
        return self

    def then_fill_non_welsh_competitive_grant_details(self):
        """Fills in the grant form with fake competitive grant details."""
        self._select_is_welsh("No")
        self.grant_name.fill(self.fake.company())
        self.grant_short_name.fill(self.fake.word()[:5])
        self.application_name.fill(self.fake.bs())
        self.grant_description.fill(self.fake.paragraph())
        self._select_grant_type("COMPETITIVE")
        self.ggis_field.fill(self.fake.uuid4())
        return self

    def then_click_save_and_return_home(self):
        """Clicks the 'Save and return home' button."""
        self.save_and_return_home.click()

        from tests.e2e.pages.dashboard_page import DashboardPage

        return DashboardPage(self.page)

    def _select_grant_type(self, type: Literal["COMPETITIVE", "UNCOMPETED", "EOI"]):
        """Selects the grant type."""
        self.grant_type.get_by_role("radio", name=type).check()
        return self

    def _select_is_welsh(self, option: Literal["Yes", "No"]):
        """Selects whether the grant is available in Welsh."""
        self.is_welsh.get_by_role("radio", name=option).check()
        return self
