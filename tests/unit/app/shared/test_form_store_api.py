from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask

from app.shared.form_store_api import FormStoreAPIService


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
            "configuration": {"key": "value"},
            "hash": "12345",
        }
        mock_get.return_value = mock_response

        service = FormStoreAPIService()
        form_config = service.get_published_form("test-form")

        assert form_config == {"key": "value"}
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
