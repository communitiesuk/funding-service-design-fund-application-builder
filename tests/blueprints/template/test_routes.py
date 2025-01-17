import pytest

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
    assert '<a href="#" role="button" draggable="false" class="govuk-button" data-module="govuk-button">' in html, (
        "Button component is missing"
    )

    # Table component availability check
    assert '<thead class="govuk-table__head">' in html, "Table is missing"
    assert '<th scope="col" class="govuk-table__header">Template name</th>' in html, "Template Name header is missing"
    assert '<th scope="col" class="govuk-table__header">Task name</th>' in html, "Tasklist Name header missing"
    assert '<th scope="col" class="govuk-table__header"></th>' in html, "Action header missing"
    assert "asset-information" in html, "Template name is missing"
    assert '<td class="govuk-table__cell">Apply for funding to save an asset in your community</td>' in html, (
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
    assert "Task title" in html, "Summary title is missing"
    assert "Template JSON file" in html, "Summary title is missing"

    # table data
    assert "About your organization template" in html, "Template name is missing"
    assert "About your organisation" in html, "Task title is missing"
    assert "about-your-org" in html, "Template JSON name is missing"
    assert '<a class="govuk-link govuk-link--no-visited-state" href="#">Change</a>' in html, "Change action is missing"

    # Detail component availability check
    assert "View template questions" in html, "View template questions is missing"
