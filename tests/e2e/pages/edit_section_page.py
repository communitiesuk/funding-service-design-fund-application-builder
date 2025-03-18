import random

from playwright.sync_api import Page, expect

from tests.e2e.pages.page_base import PageBase


class EditSectionPage(PageBase):
    def __init__(self, page: Page, base_url: str = None, metadata=None):
        super().__init__(page, base_url=base_url, metadata=metadata)
        # Initialize locators
        self.title = self.page.get_by_role("heading", name="Edit section")
        self.add_a_task = self.page.get_by_role("combobox", name="Add a task")
        self.add = self.page.get_by_role("button", name="Add")
        self.save_and_continue = self.page.get_by_role("button", name="Save and continue")

    def when_add_template(self):
        self.add_a_task.wait_for(state="visible")
        options = [
            {"label": opt.text_content(), "value": opt.get_attribute("value")}
            for opt in self.add_a_task.locator("option").all()[1:]
        ]
        template_name = self.metadata.get("template_name") if self.metadata else None
        selected_template = next(
            (
                opt
                for opt in options
                if template_name and template_name.lower() in (opt["label"] + opt["value"]).lower()
            ),
            random.choice(options),
        )
        self.add_a_task.select_option(value=selected_template["value"])
        return self

    def when_click_add(self):
        self.add.click()
        return self

    def when_click_save_and_continue(self):
        """Clicks the 'Add new grant' button."""
        self.save_and_continue.click()
        from tests.e2e.pages.build_application_page import BuildApplicationPage

        return BuildApplicationPage(self.page, metadata=self.metadata)

    def then_verify_on_edit_section(self):
        expect(self.title).to_be_visible()
        return self
