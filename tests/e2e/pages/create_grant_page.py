from typing import Literal

from playwright.sync_api import Locator, Page

from tests.e2e.pages.page_base import PageBase


class CreateGrantPage(PageBase):
    is_welsh: Locator
    grant_name: Locator
    grant_short_name: Locator
    application_name: Locator
    grant_description: Locator
    grant_type: Locator
    ggis_field: Locator
    save_and_continue: Locator
    cancel: Locator
    save_and_return_home: Locator

    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url)

    def when_goto_create_grant_page(self):
        if self.base_url:
            self.page.goto(f"{self.base_url}/grants/create")

    def then_load_components_on_create_grant_page(self):
        self.is_welsh = self.page.get_by_role("group", name="Is this grant available in Welsh?")
        self.grant_name = self.page.get_by_role("textbox", name="Grant name")
        self.grant_short_name = self.page.get_by_role("textbox", name="Grant short name")
        self.application_name = self.page.get_by_role("textbox", name="Application name")
        self.grant_description = self.page.get_by_role("textbox", name="Grant description")
        self.grant_type = self.page.get_by_role("group", name="Funding type")
        self.ggis_field = self.page.get_by_role("textbox", name="GGIS scheme reference number")

        self.save_and_continue = self.page.get_by_role("button", name="Save and continue")
        self.cancel = self.page.get_by_role("link", name="Cancel")
        self.save_and_return_home = self.page.get_by_role("button", name="Save and return home")

    def _select_grant_type(self, type: Literal["COMPETITIVE", "UNCOMPETED", "EOI"]):
        self.grant_type.get_by_role("radio", name=type).check()

    def _select_is_welsh(self, type: Literal["Yes", "No"]):
        self.is_welsh.get_by_role("radio", name=type).check()

    def then_fill_non_welsh_competitive_grant_details(self):
        self._select_is_welsh("No")
        self.grant_name.fill(self.fake.company())
        self.grant_short_name.fill(self.fake.word()[:5])
        self.application_name.fill(self.fake.bs())
        self.grant_description.fill(self.fake.paragraph())
        self._select_grant_type("COMPETITIVE")
        self.ggis_field.fill(self.fake.uuid4())

    def then_click_save_and_return_home(self):
        self.save_and_return_home.click()
