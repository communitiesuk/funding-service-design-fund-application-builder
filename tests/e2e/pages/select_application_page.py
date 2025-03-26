import random

from playwright.sync_api import Locator, Page, expect

from tests.e2e.pages.build_application_page import BuildApplicationPage
from tests.e2e.pages.page_base import PageBase


class SelectApplicationPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.select_application: Locator = self.page.get_by_role("combobox", name="Select or create an application")
        self.continue_btn: Locator = self.page.get_by_role("button", name="Continue")

    def when_select_a_application(self):
        self.select_application.wait_for(state="visible")
        self.page.query_selector_all("select option")
        application_options = [
            {"label": opt.text_content(), "value": opt.get_attribute("value")}
            for opt in self.select_application.locator("option").all()[1:]
        ]
        application_name = self.metadata.get("application_name")
        available_application_names = [option["value"] for option in application_options]
        if application_name and application_name in available_application_names:
            self.select_application.select_option(value=application_name)
        else:
            self.select_application.select_option(value=random.choice(application_options)["value"])
        return self

    def when_click_continue(self):
        self.continue_btn.click()
        return self

    def then_verify_on_select_application(self):
        expect(self.select_application).to_be_visible()
        return self

    def then_expect_build_application(self):
        return BuildApplicationPage(self.page, metadata=self.metadata)
