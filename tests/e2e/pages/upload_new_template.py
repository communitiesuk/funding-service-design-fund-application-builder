from pathlib import Path

from playwright.sync_api import Page, expect

from tests.e2e.pages.dashboard_page import DashboardPage
from tests.e2e.pages.page_base import PageBase


class UploadNewTemplatePage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Upload a new template")
        self.template_name = self.page.get_by_role("textbox", name="Template name", exact=True)
        self.task_name = self.page.get_by_role("textbox", name="Task name", exact=True)
        self.upload_file = self.page.get_by_label("Upload a file")
        self.save_and_continue = self.page.get_by_role("button", name="Save and continue")
        self.save_and_return_home = self.page.get_by_role("button", name="Save and return home")

    def given_user_is_on_templates(self):
        """Navigates to the Templates page and waits for it to load."""
        if self.base_url:
            self.page.goto(f"{self.base_url}/templates")
        return self

    def when_click_save_and_continue(self):
        """Clicks the 'Add new grant' button."""
        self.save_and_continue.click()
        from tests.e2e.pages.templates_page import TemplatesPage

        return TemplatesPage(self.page, metadata=self.metadata)

    def when_click_upload_file(self):
        """Clicks the 'Upload a file' button."""
        _template = str(Path(__file__).parent.parent) + "/fixtures/dataset-information.json"
        self.upload_file.set_input_files(_template)
        return self

    def when_adding_template_details(self):
        self.template_name_txt = f"E2E-{self.fake.name()}"
        self.update_metadata("template_name", self.template_name_txt)
        self.template_name.fill(self.template_name_txt)
        self.task_name.fill(f"E2E-{self.fake.name()}")
        return self

    def when_click_save_and_return_home(self):
        self.save_and_return_home.click()
        return DashboardPage(self.page, metadata=self.metadata)

    def then_verify_on_upload_new_template(self):
        expect(self.title).to_be_visible()
        return self
