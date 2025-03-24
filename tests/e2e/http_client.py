from typing import Literal

from tests.e2e.pages.page_base import PageBase


class HttpClient:
    base_url: str

    def __init__(self, base_url: str):
        self.base_url = base_url

    def delete(self, page_base: PageBase, delete_type: Literal["grants", "templates"]):
        if delete_type == "grants":
            uuid = page_base.metadata.get("grant_id")
            assert uuid is not None, "Grant id is not available"
        else:
            uuid = page_base.metadata.get("template_id")
            assert uuid is not None, "Template id is not available"
        response = page_base.page.request.fetch(
            f"{self.base_url}/{delete_type}/{uuid}",
            method="DELETE",
        )
        assert response.status == 204, f"Error deleting {delete_type}"
