import uuid
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup
from flask import g

from app.db.models import Form
from tests.helpers import submit_form


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user", "db_with_templates")
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
    assert "funding to save an asset in your community" in html, "Tasklist name and table component is missing"
    assert 'Preview <span class="govuk-visually-hidden">asset-information form</span> in a new tab</a>' in html, (
        "Preview action is missing"
    )


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user", "seed_dynamic_data")
def test_template_details_view(flask_test_client, seed_dynamic_data):
    form: Form = seed_dynamic_data["forms"][0]

    response = flask_test_client.get(
        f"/templates/{form.form_id}",
    )

    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Title component availability check
    assert "Back" in html, "Back button is missing"
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_template_create_get_form(flask_test_client):
    response = flask_test_client.get("/templates/create")
    assert response.status_code == 200
    assert b"Upload a new template" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_template_create_invalid_data(flask_test_client):
    response = flask_test_client.post("/templates/create", data={})
    assert response.status_code == 200
    assert b"Enter the template name" in response.data
    assert b"Enter the task name" in response.data
    assert b"Choose a template file" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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
        assert b"Upload a valid JSON file" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user", "clean_db")
def test_template_create_success(flask_test_client, clean_db):
    flask_test_client.get("/templates/create")
    with flask_test_client.session_transaction():
        filename = "asset-information.json"
        file_path = Path("tests") / "test_data" / filename
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
@patch("app.blueprints.template.routes.flash_message")
@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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
@patch("app.blueprints.template.routes.flash_message")
@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_edit_template_post_update_without_actions(
    mock_flash_message, mock_json_import, mock_delete_form, mock_update_form, mock_get_form_by_id, flask_test_client
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
        mock_update_form.return_value = Form(
            form_id=form_mock_id,
            section_id=uuid.uuid4(),
            section_index=1,
            name_in_apply_json={"en": "Updated Template"},
        )
        response = flask_test_client.post(f"/templates/{form_id}/edit", data=form_data, follow_redirects=True)
        assert response.status_code == 200
        mock_update_form.assert_called_once_with(
            form_id=form_mock_id,
            form_name="Updated Tasklist",
            template_name="Updated Template",
            form_json=None,  # Assuming no file upload in this case
        )
        mock_flash_message.assert_called_with("Template updated")


@patch("app.blueprints.template.routes.get_form_by_id")
@patch("app.blueprints.template.routes.update_form")
@patch("app.blueprints.template.routes.redirect")
@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_edit_template_post_update_with_actions_template_table(
    mock_redirect, mock_update_form, mock_get_form_by_id, flask_test_client
):
    form_mock_id = uuid.uuid4()
    form_id = str(form_mock_id)
    flask_test_client.get(f"/templates/{form_id}/edit?actions=template_table")
    with flask_test_client.session_transaction():
        form_data = {
            "template_name": "Updated Template",
            "tasklist_name": "Updated Tasklist",
            "save_and_continue": "true",
            "csrf_token": g.csrf_token,
        }
        mock_update_form.return_value = Form(
            form_id=form_mock_id,
            section_id=uuid.uuid4(),
            section_index=1,
            name_in_apply_json={"en": "Updated Template"},
        )
        response = flask_test_client.post(
            f"/templates/{form_id}/edit?actions=template_table", data=form_data, follow_redirects=True
        )
        assert response.status_code == 200
        mock_update_form.assert_called_once_with(
            form_id=form_mock_id,
            form_name="Updated Tasklist",
            template_name="Updated Template",
            form_json=None,  # Assuming no file upload in this case
        )
        mock_redirect.assert_called_once_with("/templates")


@patch("app.blueprints.template.routes.get_form_by_id")
@patch("app.blueprints.template.routes.update_form")
@patch("app.blueprints.template.routes.flash_message")
@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_edit_template_post_with_file_without_actions(
    mock_flash_message, mock_update_form, mock_get_form_by_id, flask_test_client
):
    form_mock_id = uuid.uuid4()
    form_id = str(form_mock_id)
    flask_test_client.get(f"/templates/{form_id}/edit")
    with flask_test_client.session_transaction():
        file_path = Path("tests") / "test_data" / "asset-information.json"
        form_data = {
            "template_name": "Updated Template",
            "tasklist_name": "Updated Tasklist",
            "file": (open(file_path, "rb"), "org-info.json"),
            "save_and_continue": "true",
            "csrf_token": g.csrf_token,
        }
        flask_test_client.post(f"/templates/{form_id}/edit", data=form_data, follow_redirects=True)
        mock_update_form.assert_called_once()
        mock_flash_message.assert_called_with("Template updated")


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user", "seed_dynamic_data")
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
    assert "Organisation Name" in html, "Page title is missing"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_template_search_functionality(flask_test_client, _db):
    test_template = Form(
        form_id=uuid.uuid4(),
        name_in_apply_json={"en": "SpecificTestTemplateTask"},
        template_name="SpecificTestTemplate_QWE789",
        is_template=True,
        section_index=1,
        runner_publish_name="specific-test-template",
    )
    _db.session.add(test_template)
    _db.session.commit()

    try:
        response = flask_test_client.get("/templates")
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        # Find label and button
        search_label = soup.find("label", {"for": "search"})
        assert search_label is not None
        assert "Search templates" in search_label.text

        search_button = soup.find("button", {"class": "govuk-button--success"})
        assert search_button is not None
        assert "Search" in search_button.text

        # Test 1: No search term - should show all results including our test template
        response = flask_test_client.get("/templates")
        soup = BeautifulSoup(response.data, "html.parser")
        rows = soup.select("tbody tr")
        assert len(rows) > 0
        template_names = [a.text for a in soup.select("tbody a.govuk-link")]
        assert "SpecificTestTemplate_QWE789" in template_names

        # Test 2: Search for prefix
        response = flask_test_client.get("/templates?search=SpecificTest")
        soup = BeautifulSoup(response.data, "html.parser")
        assert soup.find("input", {"id": "search"}).get("value") == "SpecificTest"
        assert soup.find("a", string=lambda text: text and "Clear search" in text)
        rows = soup.select("tbody tr")
        assert len(rows) > 0
        template_names = [a.text for a in soup.select("tbody a.govuk-link")]
        assert "SpecificTestTemplate_QWE789" in template_names

        # Test 3: Search for substring
        response = flask_test_client.get("/templates?search=QWE789")
        soup = BeautifulSoup(response.data, "html.parser")
        rows = soup.select("tbody tr")
        assert len(rows) > 0
        template_names = [a.text for a in soup.select("tbody a.govuk-link")]
        assert "SpecificTestTemplate_QWE789" in template_names

        # Test 4: Search with different case
        response = flask_test_client.get("/templates?search=specifictest")
        soup = BeautifulSoup(response.data, "html.parser")
        rows = soup.select("tbody tr")
        assert len(rows) > 0
        template_names = [a.text for a in soup.select("tbody a.govuk-link")]
        assert "SpecificTestTemplate_QWE789" in template_names

        # Test 5: No matches
        response = flask_test_client.get("/templates?search=NoMatchingTemplateHere")
        soup = BeautifulSoup(response.data, "html.parser")
        rows = soup.select("tbody tr")
        assert len(rows) == 0

    finally:
        # Clean up test data
        _db.session.delete(test_template)
        _db.session.commit()


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user", "seed_dynamic_data")
def test_template_delete(flask_test_client, seed_dynamic_data):
    form: Form = seed_dynamic_data["forms"][0]

    response = flask_test_client.get(
        f"/templates/{form.form_id}",
    )

    assert response.status_code == 200

    delete_template_link = f"/templates/{form.form_id}/delete"
    confirmation_response = flask_test_client.get(delete_template_link)

    soup = BeautifulSoup(confirmation_response.data, "html.parser")
    confirmation_heading = soup.find("h1", class_="govuk-panel__title")
    assert confirmation_response.status_code == 200
    assert confirmation_heading.text == "Are you sure you want to delete this template?"

    response = submit_form(
        flask_test_client, delete_template_link, data={"csrf_token": g.csrf_token}, follow_redirects=True
    )
    assert response.status_code == 200
