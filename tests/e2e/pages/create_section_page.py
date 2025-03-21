from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class CreateSectionPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Create section")
        self.section_name_txt = self.page.get_by_role("textbox", name="Section name")
        self.save_and_continue = self.page.get_by_role("button", name="Save and continue")

    def when_fill_section_details(self):
        section_name = self.fake.word()
        self.update_metadata("sections", [section_name])
        self.section_name_txt.fill(section_name)
        return self

    def when_save_and_continue(self):
        self.save_and_continue.click()
        from tests.e2e.pages.build_application_page import BuildApplicationPage

        return BuildApplicationPage(self.page, base_url=self.base_url, metadata=self.metadata)

    def then_verify_on_create_section(self):
        expect(self.title).to_be_visible()
        return self
