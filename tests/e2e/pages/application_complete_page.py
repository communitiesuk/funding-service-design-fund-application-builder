from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class CompleteApplicationPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        self.download_data = None
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Application marked as complete")
        self.download = self.page.get_by_role("link", name="Download the application ZIP file")

    def then_verify_on_application_complete(self):
        expect(self.title).to_be_visible()
        return self

    def when_click_download(self):
        with self.page.expect_download() as download_info:
            self.download.click()
            self.download_data = download_info.value
        return self

    def then_validate_download_success(self):
        assert self.download_data is not None, "Download data is missing"
        assert self.download_data.failure() is None, "Download was not successful"
        return self
