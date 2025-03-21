from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class TemplatesPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Templates")
        self.upload_template = self.page.get_by_role("button", name="Upload template")

    def given_user_is_on_templates(self):
        """Navigates to the Templates page and waits for it to load."""
        if self.base_url:
            self.page.goto(f"{self.base_url}/templates")
        return self

    def when_click_upload_template(self):
        """Clicks the 'Add new grant' button."""
        self.upload_template.click()
        from tests.e2e.pages.upload_new_template import UploadNewTemplatePage

        return UploadNewTemplatePage(self.page, base_url=self.base_url, metadata=self.metadata)

    def then_verify_on_templates(self):
        expect(self.title).to_be_visible()
        return self
