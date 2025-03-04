import random
import string

from playwright.sync_api import Locator, Page

from tests.e2e.pages.page_base import PageBase


class CreateApplicationPage(PageBase):
    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url)
        # Initialize locators
        self.application_round: Locator = self.page.get_by_role("textbox", name="Application round", exact=True)
        self.round_short_name: Locator = self.page.get_by_role("textbox", name="Round short name", exact=True)

        self.application_round_open = page.get_by_role("group", name="Application round opens", exact=True)
        self.application_round_close = page.get_by_role("group", name="Application round closes", exact=True)
        self.application_reminder = page.get_by_role("group", name="Application reminder email", exact=True)
        self.assessment_open = page.get_by_role("group", name="Assessment opens", exact=True)
        self.assessment_close = page.get_by_role("group", name="Assessment closes", exact=True)

        self.prospectus_link = page.get_by_role("textbox", name="Prospectus link", exact=True)
        self.privacy_notice_link = page.get_by_role("textbox", name="Privacy notice link", exact=True)
        self.project_name_field_id = page.get_by_role("textbox", name="Project name field ID", exact=True)

        self.save_and_continue: Locator = self.page.get_by_role("button", name="Save and continue")
        self.cancel: Locator = self.page.get_by_role("link", name="Cancel")
        self.save_and_return_home: Locator = self.page.get_by_role("button", name="Save and return home")

    def then_fill_application_details(self):
        self.application_name = self.fake.sentence(nb_words=3)
        self.application_round.fill(self.application_name)
        self.round_short_name.fill("".join(random.choices(string.ascii_letters + string.digits, k=6)))
        self._fill_date_time_field(self.application_round_open)
        self._fill_date_time_field(self.application_round_close)
        self._fill_date_time_field(self.application_reminder)
        self._fill_date_time_field(self.assessment_open)
        self._fill_date_time_field(self.assessment_close)
        self.prospectus_link.fill(self.fake.url())
        self.privacy_notice_link.fill(self.fake.url())
        self.project_name_field_id.fill(self.fake.uuid4())
        return self

    def then_click_save_and_return_home(self):
        self.save_and_return_home.click()
        from tests.e2e.pages.dashboard_page import DashboardPage

        return DashboardPage(self.page)

    def _fill_date_time_field(self, fieldset: Locator):
        # Generate fake date and time values
        fake_day = str(self.fake.random_int(min=1, max=28))
        fake_month = str(self.fake.random_int(min=1, max=12))
        fake_year = str(self.fake.random_int(min=2024, max=2030))
        fake_hour = str(self.fake.random_int(min=0, max=23))
        fake_minute = str(self.fake.random_int(min=0, max=59))
        # Fill the fields with fake data
        fieldset.get_by_role("textbox", name="Day").fill(fake_day)
        fieldset.get_by_role("textbox", name="Month").fill(fake_month)
        fieldset.get_by_role("textbox", name="Year").fill(fake_year)
        fieldset.get_by_role("textbox", name="Hour").fill(fake_hour)
        fieldset.get_by_role("textbox", name="Minute").fill(fake_minute)
