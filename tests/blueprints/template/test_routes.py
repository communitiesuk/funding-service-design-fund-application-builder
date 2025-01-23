import os
import uuid
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from flask import g

from app.db.models import Form


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user", "db_with_templates")
def test_generalized_table_template_with_existing_templates(flask_test_client):
    response = flask_test_client.get(
        "/templates", follow_redirects=True, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Title component availability check
    assert '<h1 class="govuk-heading-l">' in html, "Heading title component is missing"
    assert "Templates" in html, "Heading title is missing"

    # Description component availability check
    assert "Form Designer (opens in a new tab)" in html, "Title link is missing"

    # title link
    assert '<p class="govuk-body">' in html, "Description component is missing"
    assert "Form Designer (opens in a new tab)" in html, "Description is missing"

    # Detail component availability check
    assert '<span class="govuk-details__summary-text">' in html, "Detail summary drop down title component is missing"
    assert "Creating new templates" in html, "Detail summary drop down title is missing"
    assert "You should use existing templates for standard application questions." in html, (
        "Detail summary description is missing"
    )
    assert '<div class="govuk-details__text">' in html, "Detail summary description component is missing"

    # Button component availability check
    assert "Upload template" in html, "Button text is missing"
    assert (
        '<a href="/templates/create" role="button" draggable="false" class="govuk-button" data-module="govuk-button">'
        in html
    ), "Button component is missing"

    # Table component availability check
    assert '<thead class="govuk-table__head">' in html, "Table is missing"
    assert '<th scope="col" class="govuk-table__header">Template name</th>' in html, "Template Name header is missing"
    assert '<th scope="col" class="govuk-table__header">Task name</th>' in html, "Tasklist Name header missing"
    assert '<th scope="col" class="govuk-table__header"></th>' in html, "Action header missing"
    assert "asset-information" in html, "Template name is missing"
    assert "Apply for funding to save an asset in your community" in html, (
        "Tasklist name and table component is missing"
    )
    assert "Edit details" in html, "Edit action is missing"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user", "seed_dynamic_data")
def test_template_details_view(flask_test_client, seed_dynamic_data):
    form: Form = seed_dynamic_data["forms"][0]

    response = flask_test_client.get(
        f"/templates/{form.form_id}",
    )

    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Title component availability check
    assert '<a href="/templates" class="govuk-back-link">Back</a>' in html, "Back button is missing"
    assert "Preview template (opens in a new tab)" in html, "Preview template is missing"
    assert f"/preview/{form.form_id}" in html, "Preview link is missing"

    # table titles
    assert "Template name" in html, "Summary title is missing"
    assert "Task name" in html, "Summary title is missing"
    assert "Template JSON file" in html, "Summary title is missing"

    # table data
    assert "About your organization template" in html, "Template name is missing"
    assert "About your organisation" in html, "Task title is missing"
    assert "Change" in html, "Change action is missing"

    # Detail component availability check
    assert "View template questions" in html, "View template questions is missing"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_template_create_get_form(flask_test_client):
    response = flask_test_client.get("/templates/create")
    assert response.status_code == 200
    assert b"Add a new template" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_template_create_invalid_data(flask_test_client):
    response = flask_test_client.post("/templates/create", data={})
    assert response.status_code == 200
    assert b"This field is required" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_template_create_already_existing_template(flask_test_client):
    flask_test_client.get("/templates/create")
    with flask_test_client.session_transaction():
        with patch("app.blueprints.template.routes.get_form_by_template_name", return_value=True):
            data = {
                "template_name": "existing_template",
                "tasklist_name": "tasklist1",
                "file": (BytesIO(b'{"key": "value"}'), "test.json"),
                "csrf_token": g.csrf_token,
            }
            response = flask_test_client.post("/templates/create", data=data)
            assert response.status_code == 200
            assert b"Template name already exists" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_template_create_invalid_json_file(flask_test_client):
    flask_test_client.get("/templates/create")
    with flask_test_client.session_transaction():
        data = {
            "template_name": "existing_template",
            "tasklist_name": "tasklist1",
            "file": (BytesIO(b'{"key": "value"}'), "test.json"),
            "csrf_token": g.csrf_token,
        }
        response = flask_test_client.post("/templates/create", data=data)
        assert response.status_code == 200
        assert b"Please upload valid JSON file" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user", "clean_db")
def test_template_create_success(flask_test_client, clean_db):
    flask_test_client.get("/templates/create")
    with flask_test_client.session_transaction():
        test_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        test_data_dir = os.path.join(test_root, "test_data")
        file_path = os.path.join(test_data_dir, "asset-information.json")
        data = {
            "template_name": f"existing_template-{uuid.uuid4()}",
            "tasklist_name": f"tasklist1-{uuid.uuid4()}",
            "file": (open(file_path, "rb"), "org-info.json"),
            "csrf_token": g.csrf_token,
        }
        response = flask_test_client.post("/templates/create", data=data)
        assert response.status_code == 302

        # Check the flash messages (if there are any)
        with flask_test_client.session_transaction() as session:
            flash_messages = session.get("_flashes", [])
            assert any("Template uploaded" in msg[1] for msg in flash_messages)


@patch("app.blueprints.template.routes.get_form_by_id")
@patch("app.blueprints.template.routes.update_form")
@patch("app.blueprints.template.routes.delete_form")
@patch("app.blueprints.template.routes.json_import")
@patch("app.blueprints.template.routes.flash")
@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_edit_template_get(
    mock_flash, mock_json_import, mock_delete_form, mock_update_form, mock_get_form_by_id, flask_test_client
):
    mock_form = MagicMock()
    mock_form.template_name = "Test Template"
    mock_form.name_in_apply_json = {"en": "Test Tasklist"}
    mock_get_form_by_id.return_value = mock_form
    form_mock_id = uuid.uuid4()
    form_id = str(form_mock_id)
    response = flask_test_client.get(f"/templates/{form_id}/edit")
    assert response.status_code == 200
    assert b"Test Template" in response.data
    assert b"Test Tasklist" in response.data
    mock_get_form_by_id.assert_called_once_with(form_id=form_mock_id)


@patch("app.blueprints.template.routes.get_form_by_id")
@patch("app.blueprints.template.routes.update_form")
@patch("app.blueprints.template.routes.delete_form")
@patch("app.blueprints.template.routes.json_import")
@patch("app.blueprints.template.routes.flash")
@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_edit_template_post_update(
    mock_flash, mock_json_import, mock_delete_form, mock_update_form, mock_get_form_by_id, flask_test_client
):
    form_mock_id = uuid.uuid4()
    form_id = str(form_mock_id)
    flask_test_client.get(f"/templates/{form_id}/edit")
    with flask_test_client.session_transaction():
        form_data = {
            "template_name": "Updated Template",
            "tasklist_name": "Updated Tasklist",
            "save_and_continue": "true",
            "csrf_token": g.csrf_token,
        }
        response = flask_test_client.post(f"/templates/{form_id}/edit", data=form_data, follow_redirects=True)
        assert response.status_code == 200
        mock_update_form.assert_called_once_with(
            form_id=form_mock_id,
            new_form_config={
                "name_in_apply_json": {"en": "Updated Tasklist"},
                "template_name": "Updated Template",
            },
        )
        mock_flash.assert_called_with("Updated template Updated Template")


@patch("app.blueprints.template.routes.get_form_by_id")
@patch("app.blueprints.template.routes.update_form")
@patch("app.blueprints.template.routes.delete_form")
@patch("app.blueprints.template.routes.json_import")
@patch("app.blueprints.template.routes.flash")
@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_edit_template_post_with_file(
    mock_flash, mock_json_import, mock_delete_form, mock_update_form, mock_get_form_by_id, flask_test_client
):
    form_mock_id = uuid.uuid4()
    form_id = str(form_mock_id)
    flask_test_client.get(f"/templates/{form_id}/edit")
    with flask_test_client.session_transaction():
        test_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        test_data_dir = os.path.join(test_root, "test_data")
        file_path = os.path.join(test_data_dir, "asset-information.json")
        form_data = {
            "template_name": "Updated Template",
            "tasklist_name": "Updated Tasklist",
            "file": (open(file_path, "rb"), "org-info.json"),
            "save_and_continue": "true",
            "csrf_token": g.csrf_token,
        }
        flask_test_client.post(f"/templates/{form_id}/edit", data=form_data, follow_redirects=True)
        mock_delete_form.assert_called_once_with(form_id=form_mock_id, cascade=True)
        mock_json_import.assert_called_once()
        mock_flash.assert_called_with("Updated template Updated Template")


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user", "seed_dynamic_data")
def test_template_questions_view(flask_test_client, seed_dynamic_data):
    form: Form = seed_dynamic_data["forms"][0]

    response = flask_test_client.get(
        f"/templates/{form.form_id}/questions",
    )

    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Title component availability check
    assert "About your organization template" in html, "Template title is missing"
    assert "This template contains the following questions." in html, "Title description is missing"
