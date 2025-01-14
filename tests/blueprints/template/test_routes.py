import pytest


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
    assert "Form Designer (opens in a new tab)." in html, "Title link is missing"

    # title link
    assert '<p class="govuk-body">' in html, "Description component is missing"
    assert "Form Designer (opens in a new tab)." in html, "Description is missing"

    # Detail component availability check
    assert '<span class="govuk-details__summary-text">' in html, "Detail summary drop down title component is missing"
    assert "Using templates in applications" in html, "Detail summary drop down title is missing"
    assert (
        "You should use existing templates for standard application questions." in html
    ), "Detail summary description is missing"
    assert '<div class="govuk-details__text">' in html, "Detail summary description component is missing"

    # Button component availability check
    assert "Upload template" in html, "Button text is missing"
    assert (
        '<button type="submit" class="govuk-button" data-module="govuk-button">' in html
    ), "Button component is missing"

    # Table component availability check
    assert '<thead class="govuk-table__head">' in html, "Table is missing"
    assert '<th scope="col" class="govuk-table__header">Template name</th>' in html, "Template Name header is missing"
    assert '<th scope="col" class="govuk-table__header">Task name</th>' in html, "Tasklist Name header missing"
    assert '<th scope="col" class="govuk-table__header"></th>' in html, "Action header missing"
    assert "asset-information" in html, "Template name is missing"
    assert (
        '<td class="govuk-table__cell">Apply for funding to save an asset in your community</td>' in html
    ), "Tasklist name and table component is missing"
    assert "Edit details" in html, "Edit action is missing"
