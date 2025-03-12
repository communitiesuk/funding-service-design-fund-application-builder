from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class BuildApplicationPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Build application")
        self.add_section = self.page.get_by_role("button", name="Add section")
        self.mark_application_complete = self.page.get_by_role("link", name="Mark application complete")

    def when_click_add_section(self):
        self.add_section.click()

        from tests.e2e.pages.create_section_page import CreateSectionPage

        return CreateSectionPage(self.page, metadata=self.metadata)

    def when_click_edit_first_section(self):
        assert self.metadata.get("sections") or len(self.metadata.get("sections")) > 0, "No sections available"
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

    def when_click_down_on_section(self):
        assert self.metadata.get("sections") or len(self.metadata.get("sections")) > 0, "No sections available"
        task_element = self.page.get_by_role("heading", name=self.metadata.get("sections")[0])
        task_parent = task_element.locator("xpath=ancestor::li")
        expect(task_parent).to_be_visible()
        down_link = task_parent.get_by_role("link", name="Down")
        expect(down_link).to_be_visible()
        down_link.click()
        return self

    def when_click_up_on_section(self):
        assert self.metadata.get("sections") or len(self.metadata.get("sections")) > 0, "No sections available"
        task_element = self.page.get_by_role("heading", name=self.metadata.get("sections")[0])
        task_parent = task_element.locator("xpath=ancestor::li")
        expect(task_parent).to_be_visible()
        down_link = task_parent.get_by_role("link", name="Up")
        expect(down_link).to_be_visible()
        down_link.click()
        return self

    def then_verify_section_gone_down(self):
        first_section = self.page.locator(".task-list__new-design.govuk-\\!-margin-bottom-2").all()[1]
        first_section.get_by_role("heading", name=self.metadata.get("sections")[0]).is_visible()
        return self

    def then_verify_section_gone_up(self):
        first_section = self.page.locator(".task-list__new-design.govuk-\\!-margin-bottom-2").all()[0]
        first_section.get_by_role("heading", name=self.metadata.get("sections")[0]).is_visible()
        return self

    def and_validate_application_success_message(self):
        banner = self.page.locator(".govuk-notification-banner--success")
        expect(banner.get_by_role("heading", name="New application created")).to_be_visible()
        expect(banner.locator("a")).to_have_count(1)
        application_link_name = banner.locator("a").first.inner_text()
        application_name_metadata = self.metadata.get("application_name")
        assert application_link_name == f"View {application_name_metadata}"
        return self

    def and_verify_on_build_application(self):
        return self.then_verify_on_build_application()
