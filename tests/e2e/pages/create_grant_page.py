import random
import string
from typing import Literal

from playwright.sync_api import Locator, Page, expect

from tests.e2e.pages.page_base import PageBase


class CreateGrantPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Add a new grant")
        self.is_welsh: Locator = self.page.get_by_role("group", name="Is this grant available in Welsh?")
        self.grant_name_tb: Locator = self.page.get_by_role("textbox", name="Grant name", exact=True)
        self.grant_short_name: Locator = self.page.get_by_role("textbox", name="Grant short name", exact=True)
        self.application_name: Locator = self.page.get_by_role("textbox", name="Application name", exact=True)
        self.grant_description: Locator = self.page.get_by_role("textbox", name="Grant description", exact=True)
        self.grant_type: Locator = self.page.get_by_role("group", name="Funding type")
        self.ggis_field: Locator = self.page.get_by_role("textbox", name="GGIS scheme reference number")

        self.save_and_continue: Locator = self.page.get_by_role("button", name="Save and continue")
        self.cancel: Locator = self.page.get_by_role("link", name="Cancel")
        self.save_and_return_home: Locator = self.page.get_by_role("button", name="Save and return home")

    def when_fill_non_welsh_competitive_grant_details(self):
        """Fills in the grant form with fake competitive grant details."""
        grant_name = f"E2E-{self.fake.company()}"
        self.update_metadata("grant_name", grant_name)
        self._select_is_welsh("No")
        self.grant_name_tb.fill(grant_name)
        self.grant_short_name.fill("".join(random.choices(string.ascii_letters + string.digits, k=6)))
        self.application_name.fill(self.fake.bs())
        self.grant_description.fill(self.fake.paragraph())
        self._select_grant_type("COMPETITIVE")
        self.ggis_field.fill(self.fake.uuid4())
        return self

    def when_click_save_and_return_home(self):
        """Clicks the 'Save and return home' button."""
        self.save_and_return_home.click()
        from tests.e2e.pages.dashboard_page import DashboardPage

        return DashboardPage(self.page, base_url=self.base_url, metadata=self.metadata)

    def when_click_save_and_continue(self):
        """Clicks the 'Save and continue' button."""
        self.save_and_continue.click()
        from tests.e2e.pages.create_application_page import CreateApplicationPage

        return CreateApplicationPage(self.page, base_url=self.base_url, metadata=self.metadata)

    def then_verify_on_create_grant(self):
        expect(self.title).to_be_visible()
        return self

    def _select_grant_type(self, type: Literal["COMPETITIVE", "UNCOMPETED", "EOI"]):
        """Selects the grant type."""
        self.grant_type.get_by_role("radio", name=type).check()
        return self

    def _select_is_welsh(self, option: Literal["Yes", "No"]):
        """Selects whether the grant is available in Welsh."""
        self.is_welsh.get_by_role("radio", name=option).check()
        return self
