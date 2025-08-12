import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from app.shared.json_validation import validate_form_json

# Path to test data directory
TEST_DATA_DIR = Path(__file__).parent.parent.parent.parent / "test_data"


def load_test_json(filename):
    """Helper function to load JSON test files."""
    file_path = TEST_DATA_DIR / filename
    with open(file_path, "r") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "filename",
    [
        "asset-information.json",
        "dataset-information.json",
        "funding-required-cof-25.json",
        "organisation-and-local-authority.json",
        "projects.json",
    ],
)
def test_valid_json_files(filename):
    """Test that all valid JSON files pass validation."""
    form_data = load_test_json(filename)

    # Should not raise any exception
    validate_form_json(form_data)


def test_missing_required_field():
    """Test that missing required fields raise ValidationError."""
    invalid_form = {
        "name": "Test Form",
        # Missing startPage
        "sections": [],
        "pages": [],
        "lists": [],
        "conditions": [],
        "outputs": [],
        "skipSummary": False,
    }

    with pytest.raises(ValidationError):
        validate_form_json(invalid_form)


def test_invalid_page_structure():
    """Test that pages with missing required fields fail validation."""
    invalid_form = {
        "name": "Test Form",
        "startPage": "/start",
        "sections": [],
        "pages": [
            {
                "path": "/page1",
                # Missing title and components
            }
        ],
        "lists": [],
        "conditions": [],
        "outputs": [],
        "skipSummary": False,
    }

    with pytest.raises(ValidationError):
        validate_form_json(invalid_form)


def test_wrong_data_types():
    """Test that wrong data types fail validation."""
    invalid_form = {
        "name": 123,  # Should be string
        "startPage": "/start",
        "sections": "not_an_array",  # Should be array
        "pages": [],
        "lists": [],
        "conditions": [],
        "outputs": [],
        "skipSummary": "not_boolean",  # Should be boolean
    }

    with pytest.raises(ValidationError):
        validate_form_json(invalid_form)


def test_minimal_valid_form():
    """Test the minimal valid form structure."""
    minimal_form = {
        "name": "Minimal Form",
        "startPage": "/start",
        "sections": [],
        "pages": [{"path": "/start", "title": "Start Page", "components": []}],
        "lists": [],
        "conditions": [],
        "outputs": [],
        "skipSummary": False,
    }

    # Should not raise any exception
    validate_form_json(minimal_form)
