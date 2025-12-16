import random
import re
import string
from datetime import datetime, timedelta

from playwright.sync_api import Locator, Page, expect

from tests.e2e.pages.page_base import PageBase


class CreateApplicationPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Create a new application")
        self.grant_name = self.page.locator("text=Grant:").text_content()
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

        self.application_fields_download_available = page.get_by_role(
            "group", name="Do you want to allow assessors to download application fields?"
        )
        self.display_logo_on_pdf_exports = page.get_by_role("group", name="Do you want to have the MHCLG logo on PDFs?")
        self.mark_as_complete_enabled = page.get_by_role(
            "group", name="Do you want applicants to mark sections as complete?"
        )
        self.is_expression_of_interest = page.get_by_role(
            "group", name="Is this application round an expression of interest?"
        )
        self.has_feedback_survey = page.get_by_role("group", name="Do you want to include a feedback survey?")
        self.is_feedback_survey_optional = page.get_by_role("group", name="Is the feedback survey optional?")
        self.has_research_survey = page.get_by_role("group", name="Do you want to include a research survey?")
        self.is_research_survey_optional = page.get_by_role("group", name="Is the research survey optional?")
        self.eligibility_config = page.get_by_role(
            "group", name="Do applicants need to pass eligibility questions before applying?"
        )
        self.send_incomplete_application_emails = page.get_by_role(
            "group",
            name=(
                "Do you want to automatically send notification emails for incomplete applications after the deadline?"
            ),
            exact=True,
        )

        self.save_and_continue: Locator = self.page.get_by_role("button", name="Save and continue")
        self.cancel: Locator = self.page.get_by_role("link", name="Cancel")
        self.save_and_return_home: Locator = self.page.get_by_role("button", name="Save and return home")

    def when_fill_application_details(self):
        application_name = f"E2E-{self.fake.sentence(nb_words=3)}"
        self.update_metadata("application_name", application_name)
        self.application_round.fill(application_name)
        self.round_short_name.fill("".join(random.choices(string.ascii_letters + string.digits, k=6)))

        # Ensure date logic consistency using Faker
        application_open = self._fill_date_time_field(self.application_round_open)
        self._fill_date_time_field(self.application_round_close, after_date=application_open)
        self._fill_date_time_field(self.application_reminder)
        assessment_open = self._fill_date_time_field(self.assessment_open)
        self._fill_date_time_field(self.assessment_close, after_date=assessment_open)

        self.prospectus_link.fill(self.fake.url())
        self.privacy_notice_link.fill(self.fake.url())
        self.project_name_field_id.fill(self.fake.uuid4())

        self._fill_radio_buttons()

        return self

    def _fill_radio_buttons(self):
        """Fill all required radio button fields with default values"""
        self.application_fields_download_available.get_by_role("radio", name="Yes").check()
        self.display_logo_on_pdf_exports.get_by_role("radio", name="Yes").check()
        self.mark_as_complete_enabled.get_by_role("radio", name="Yes").check()
        self.is_expression_of_interest.get_by_role("radio", name="No").check()
        self.has_feedback_survey.get_by_role("radio", name="No").check()
        self.is_feedback_survey_optional.get_by_role("radio", name="Yes").check()
        self.has_research_survey.get_by_role("radio", name="No").check()
        self.is_research_survey_optional.get_by_role("radio", name="Yes").check()
        self.eligibility_config.get_by_role("radio", name="No").check()
        self.send_incomplete_application_emails.get_by_role("radio", name="No").check()

    def when_click_save_and_return_home(self):
        self.save_and_return_home.click()
        from tests.e2e.pages.dashboard_page import DashboardPage

        return DashboardPage(self.page, metadata=self.metadata)

    def when_click_save_and_continue(self):
        self.save_and_continue.click()
        return self

    def then_expect_applications(self):
        from tests.e2e.pages.applications_page import ApplicationsPage

        return ApplicationsPage(self.page, metadata=self.metadata)

    def then_expect_build_application(self):
        from tests.e2e.pages.build_application_page import BuildApplicationPage

        return BuildApplicationPage(self.page, metadata=self.metadata)

    def then_verify_on_create_application(self):
        expect(self.title).to_be_visible()
        return self

    and_verify_on_create_application = then_verify_on_create_application

    def and_validate_grant_success_message(self):
        banner = self.page.locator(".govuk-notification-banner--success")
        expect(banner.get_by_role("heading", name="New grant added successfully")).to_be_visible()
        expect(banner.locator("a")).to_have_count(1)
        grant_name = self.metadata.get("grant_name")
        grant_link = self.page.get_by_role("link", name=f"View {grant_name}")
        expect(grant_link).to_be_visible()
        self.update_metadata("grant_id", re.search(r"[0-9a-fA-F-]{36}$", grant_link.get_attribute("href")).group(0))
        return self

    def and_verify_grant_on_create_application(self, grant_name: str):
        assert grant_name in self.grant_name, "Given grant name is not in the create application page"
        return self

    def _fill_date_time_field(self, fieldset: Locator, after_date: datetime = None):
        """Fills a date-time fieldset with a valid date, ensuring it is after a given reference date.

        Args:
            fieldset (Locator): The Playwright locator for the date-time input fields.
            after_date (datetime, optional): The earliest date allowed for the generated value.

        Returns:
            datetime: The generated date that was filled in.
        """
        start_date = after_date + timedelta(days=1) if after_date else datetime.now() + timedelta(days=1)
        date_value = self.fake.date_time_between(start_date=start_date, end_date=start_date + timedelta(days=7))

        fieldset.get_by_role("textbox", name="Day").fill(str(date_value.day))
        fieldset.get_by_role("textbox", name="Month").fill(str(date_value.month))
        fieldset.get_by_role("textbox", name="Year").fill(str(date_value.year))
        fieldset.get_by_role("textbox", name="Hour").fill(str(date_value.hour))
        fieldset.get_by_role("textbox", name="Minute").fill(str(date_value.minute))

        return date_value
