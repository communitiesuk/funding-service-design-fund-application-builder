from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

import requests
from flask import current_app, g


class FormNotFoundError(Exception):
    """Raised when a form cannot be found in the Form Store API"""

    def __init__(self, url_path: str = None, message: str = None):
        if message is not None:
            self.message = message
        elif url_path is not None:
            self.message = f"Published form not found for URL path: {url_path}"
        else:
            self.message = "Published form not found"
        super().__init__(self.message)


@dataclass
class FormResponse:
    """Base metadata for all form responses"""

    id: str
    url_path: str
    display_name: str | None
    created_at: str | None
    updated_at: str | None
    published_at: str | None
    is_published: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormResponse":
        return cls(
            id=data["id"],
            url_path=data["url_path"],
            display_name=data.get("display_name"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            published_at=data.get("published_at"),
            is_published=data["is_published"],
        )


@dataclass
class PublishedFormResponse(FormResponse):
    """Response from GET /forms/{url_path}/published endpoint"""

    published_json: dict[str, Any]
    hash: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PublishedFormResponse":
        return cls(
            id=data["id"],
            url_path=data["url_path"],
            display_name=data.get("display_name"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            published_at=data.get("published_at"),
            is_published=data["is_published"],
            published_json=data["published_json"],
            hash=data["hash"],
        )


class FormStoreAPIService:
    """Service class for interacting with the Form Store API"""

    def __init__(self):
        self.base_url = current_app.config.get("FORM_STORE_API_HOST")
        if not self.base_url:
            raise ValueError("FORM_STORE_API_HOST configuration is required")

    def get_published_forms(self) -> list[FormResponse]:
        """
        Fetch all forms from the Form Store API and filter to only those with published_json populated, with
        request-scoped caching.
        """
        # Check if we've already fetched in this request
        if hasattr(g, "_published_forms_cache"):
            return g._published_forms_cache

        try:
            response = requests.get(self.base_url, timeout=30, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            result = response.json()
            all_forms = [FormResponse.from_dict(item) for item in result]
            published_forms = [form for form in all_forms if form.is_published is True]

            # Cache in request context
            g._published_forms_cache = published_forms
            return published_forms
        except Exception as e:
            current_app.logger.error("Error fetching forms from Form Store API: %s", e)
            return []

    def get_published_form(self, url_path: str) -> PublishedFormResponse | None:
        try:
            response = requests.get(f"{self.base_url}/{url_path}/published")
            response.raise_for_status()
            result = response.json()
            return PublishedFormResponse.from_dict(result)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == HTTPStatus.NOT_FOUND:
                current_app.logger.info("Form '%s' not found", url_path)
            else:
                current_app.logger.error("Error fetching form %s from Form Store API: %s", url_path, e)
        except Exception as e:
            current_app.logger.error("Error fetching form %s from Form Store API: %s", url_path, e)
        return None

    def get_display_name_from_url_path(self, url_path: str) -> str | None:
        published_forms = self.get_published_forms()
        url_path_to_display_name = {pf.url_path: pf.display_name for pf in published_forms}
        return url_path_to_display_name.get(url_path)
