from faker import Faker
from playwright.sync_api import Page


class PageBase:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.fake = Faker()
