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
class FormDefinition:
    id: str
    url_path: str
    display_name: str | None
    created_at: str | None
    updated_at: str | None
    published_at: str | None
    is_published: bool
    draft_json: dict[str, Any] | None = None
    published_json: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormDefinition":
        return cls(**data)


@dataclass
class PublishedFormResponse:
    configuration: dict[str, Any]
    hash: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PublishedFormResponse":
        return cls(**data)


class FormStoreAPIService:
    """Service class for interacting with the Form Store API"""

    def __init__(self):
        self.base_url = current_app.config.get("FORM_STORE_API_HOST")
        if not self.base_url:
            raise ValueError("FORM_STORE_API_HOST configuration is required")

    def get_published_forms(self) -> list[FormDefinition]:
        """Fetch all forms from the Form Store API with request-scoped caching."""
        # Check if we've already fetched in this request
        if hasattr(g, "_published_forms_cache"):
            return g._published_forms_cache

        try:
            response = requests.get(self.base_url, timeout=30, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            result = response.json()
            all_forms = [FormDefinition.from_dict(item) for item in result]
            published_forms = [form for form in all_forms if form.is_published is True]

            # Cache in request context
            g._published_forms_cache = published_forms
            return published_forms
        except Exception as e:
            current_app.logger.error("Error fetching forms from Form Store API: %s", e)
            return []

    def get_published_form(self, url_path: str) -> dict[str, Any] | None:
        try:
            response = requests.get(f"{self.base_url}/{url_path}/published")
            response.raise_for_status()
            result = response.json()
            published_form_response = PublishedFormResponse.from_dict(result)
            return published_form_response.configuration
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
