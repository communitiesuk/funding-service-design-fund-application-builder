from dataclasses import dataclass
from http import HTTPStatus
from typing import Any

import requests
from flask import current_app


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
        """Fetch all forms from the Form Store API and filter to only those with published_json populated."""
        try:
            response = requests.get(self.base_url, timeout=30, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            result = response.json()
            all_forms = [FormDefinition.from_dict(item) for item in result]
            return [form for form in all_forms if form.is_published is True]
        except Exception as e:
            current_app.logger.error("Error fetching forms from Form Store API: %s", e)
            return []

    def get_published_form(self, form_name: str) -> dict[str, Any] | None:
        try:
            response = requests.get(f"{self.base_url}/{form_name}/published")
            response.raise_for_status()
            result = response.json()
            published_form_response = PublishedFormResponse.from_dict(result)
            return published_form_response.configuration
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == HTTPStatus.NOT_FOUND:
                current_app.logger.info("Form '%s' not found", form_name)
            else:
                current_app.logger.error("Error fetching form %s from Form Store API: %s", form_name, e)
        except Exception as e:
            current_app.logger.error("Error fetching form %s from Form Store API: %s", form_name, e)
        return None
