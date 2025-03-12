from faker import Faker
from playwright.sync_api import Page


class PageBase:
    def __init__(self, page: Page, base_url: str, metadata=None):
        self.page = page
        self.base_url = base_url
        self.fake = Faker()
        self.metadata = metadata or {}

    def update_metadata(self, key, value):
        """Update shared data dictionary"""
        if key in self.metadata:
            if isinstance(self.metadata[key], list) and isinstance(value, list):
                self.metadata[key].extend(value)
            else:
                self.metadata[key] = value
        else:
            self.metadata[key] = value
