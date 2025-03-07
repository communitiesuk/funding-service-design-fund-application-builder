from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class BuildApplicationPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Build application")
        self.add_section = self.page.get_by_role("button", name="Add section")

        self.view_all_application_question = self.page.get_by_role("link", name="View all application questions")
        self.download_application_zip_file = self.page.get_by_role("link", name="Download application ZIP file")
        self.mark_application_complete = self.page.get_by_role("link", name="Mark application complete")

    def when_click_add_section(self):
        self.add_section.click()

        from tests.e2e.pages.create_section_page import CreateSectionPage

        return CreateSectionPage(self.page, metadata=self.metadata)

    def when_click_edit_first_section(self):
        assert self.metadata.get("sections") or len(self.metadata.get("sections")) > 0, "No sections section available"
        task_element = self.page.get_by_role("heading", name=self.metadata.get("sections")[0])
        task_parent = task_element.locator("xpath=ancestor::li")
        expect(task_parent).to_be_visible()
        edit_button = task_parent.get_by_role("link", name="Edit")
        expect(edit_button).to_be_visible()
        edit_button.click()

        from tests.e2e.pages.edit_section_page import EditSectionPage

        return EditSectionPage(self.page, metadata=self.metadata)

    def when_click_mark_application_complete(self):
        self.mark_application_complete.click()
        from tests.e2e.pages.application_complete_page import CompleteApplicationPage

        return CompleteApplicationPage(self.page, metadata=self.metadata)

    def then_verify_on_build_application(self):
        expect(self.title).to_be_visible()
        return self
