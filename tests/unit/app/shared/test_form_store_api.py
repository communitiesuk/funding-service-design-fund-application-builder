from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask

from app.shared.form_store_api import FormStoreAPIService, PublishedFormResponse


class TestFormStoreAPIService:
    @pytest.fixture(autouse=True)
    def app_context(self):
        app = Flask(__name__)
        app.config["FORM_STORE_API_HOST"] = "http://localhost"
        with app.app_context():
            yield

    @patch("requests.get")
    def test_get_published_forms_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = [
            {
                "id": "1",
                "url_path": "form-1",
                "display_name": "Form 1",
                "is_published": True,
                "created_at": None,
                "updated_at": None,
                "published_at": None,
            },
            {
                "id": "2",
                "url_path": "form-2",
                "display_name": "Form 2",
                "is_published": False,
                "created_at": None,
                "updated_at": None,
                "published_at": None,
            },
            {
                "id": "3",
                "url_path": "form-3",
                "display_name": "Form 3",
                "is_published": True,
                "created_at": None,
                "updated_at": None,
                "published_at": None,
            },
        ]
        mock_get.return_value = mock_response

        service = FormStoreAPIService()
        forms = service.get_published_forms()

        assert len(forms) == 2
        assert forms[0].display_name == "Form 1"
        assert forms[1].display_name == "Form 3"
        mock_get.assert_called_once_with("http://localhost", timeout=30, headers={"Content-Type": "application/json"})

    @patch("requests.get")
    def test_get_published_forms_empty(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        service = FormStoreAPIService()
        forms = service.get_published_forms()

        assert len(forms) == 0

    @patch("requests.get")
    def test_get_published_forms_no_published(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = [
            {
                "id": "1",
                "url_path": "form-1",
                "display_name": "Form 1",
                "is_published": False,
                "created_at": None,
                "updated_at": None,
                "published_at": None,
            },
        ]
        mock_get.return_value = mock_response

        service = FormStoreAPIService()
        forms = service.get_published_forms()

        assert len(forms) == 0

    @patch("requests.get")
    def test_get_published_forms_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        service = FormStoreAPIService()
        forms = service.get_published_forms()

        assert len(forms) == 0

    @patch("requests.get")
    def test_get_published_form_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "url_path": "test-form",
            "display_name": "Test Form",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-02T00:00:00",
            "published_at": "2025-01-02T00:00:00",
            "is_published": True,
            "published_json": {"key": "value"},
            "hash": "12345",
        }
        mock_get.return_value = mock_response

        service = FormStoreAPIService()
        result = service.get_published_form("test-form")

        assert result is not None
        assert isinstance(result, PublishedFormResponse)
        assert result.published_json == {"key": "value"}
        assert result.hash == "12345"
        assert result.url_path == "test-form"
        assert result.display_name == "Test Form"
        mock_get.assert_called_once_with("http://localhost/test-form/published")

    @patch("requests.get")
    def test_get_published_form_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)

        service = FormStoreAPIService()
        form_config = service.get_published_form("non-existent-form")

        assert form_config is None

    @patch("requests.get")
    def test_get_published_form_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)

        service = FormStoreAPIService()
        form_config = service.get_published_form("error-form")

        assert form_config is None

    @patch("requests.get")
    def test_get_published_form_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        service = FormStoreAPIService()
        form_config = service.get_published_form("exception-form")

        assert form_config is None
