import pytest

from tests.helpers import get


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_generalized_table_template_with_empty_templates(flask_test_client):
    response = get(flask_test_client, "/templates")
    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Title component availability check
    assert ('<h1 class="govuk-heading-l">' in html), "Heading title component is missing"
    assert ('Templates' in html), "Heading title is missing"

    # Description component availability check
    assert ('<p class="govuk-body">' in html), "Description component is missing"
    assert ('Follow the step-by-step instructions to create a new grant application.' in html), "Description is missing"

    # Detail component availability check
    assert ('<span class="govuk-details__summary-text">' in html), "Detail summary drop down title component is missing"
    assert ('Using templates in applications' in html), "Detail summary drop down title is missing"
    assert (
            'This is an placeholder which will be added for the template page' in html), "Detail summary description is missing"
    assert ('<div class="govuk-details__text">' in html), "Detail summary description component is missing"

    # Button component availability check
    assert ('Open template builder' in html), "Button text is missing"
    assert (
            '<button type="submit" class="govuk-button" data-module="govuk-button">' in html), "Button component is missing"

    # Table component availability check
    assert ('<thead class="govuk-table__head">' in html), "Table is missing"
    assert ('<th scope="col" class="govuk-table__header">Template Name</th>' in html), "Template Name header is missing"
    assert ('<th scope="col" class="govuk-table__header">Tasklist Name</th>' in html), "Tasklist Name header missing"
    assert ('<th scope="col" class="govuk-table__header">URL Path</th>' in html), "URL Path header missing"
    assert ('<th scope="col" class="govuk-table__header">Action</th>' in html), "Action header missing"

    # Pagination component availability check
    assert ('<nav class="govuk-pagination" aria-label="Pagination">' in html), "Pagination component is missing"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user", "db_with_templates")
def test_generalized_table_template_with_existing_templates(flask_test_client):
    response = get(flask_test_client, "/templates")
    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Title component availability check
    assert ('<h1 class="govuk-heading-l">' in html), "Heading title component is missing"
    assert ('Templates' in html), "Heading title is missing"

    # Description component availability check
    assert ('<p class="govuk-body">' in html), "Description component is missing"
    assert (
            'Follow the step-by-step instructions to create a new grant application.' in html), "Description is missing"

    # Detail component availability check
    assert (
            '<span class="govuk-details__summary-text">' in html), "Detail summary drop down title component is missing"
    assert ('Using templates in applications' in html), "Detail summary drop down title is missing"
    assert (
            'This is an placeholder which will be added for the template page' in html), "Detail summary description is missing"
    assert ('<div class="govuk-details__text">' in html), "Detail summary description component is missing"

    # Button component availability check
    assert ('Open template builder' in html), "Button text is missing"
    assert (
            '<button type="submit" class="govuk-button" data-module="govuk-button">' in html), "Button component is missing"

    # Table component availability check
    assert ('<thead class="govuk-table__head">' in html), "Table is missing"
    assert (
            '<th scope="col" class="govuk-table__header">Template Name</th>' in html), "Template Name header is missing"
    assert (
            '<th scope="col" class="govuk-table__header">Tasklist Name</th>' in html), "Tasklist Name header missing"
    assert ('<th scope="col" class="govuk-table__header">URL Path</th>' in html), "URL Path header missing"
    assert ('<th scope="col" class="govuk-table__header">Action</th>' in html), "Action header missing"
    assert ('asset-information' in html), "Template name is missing"
    assert (
                '<td class="govuk-table__cell">Apply for funding to save an asset in your community</td>' in html), "Tasklist name and table component is missing"
    assert (
                '<td class="govuk-table__cell">asset-information</td>' in html), "URL path header is not available and table component is missing"
    assert ('Edit' in html), "Edit action is missing"
    assert ('Delete' in html), "Delete action is missing"

    # Table data testing
    assert ('<th scope="col" class="govuk-table__header">Action</th>' in html), "Action header missing"

    # Pagination component availability check
    assert ('<nav class="govuk-pagination" aria-label="Pagination">' in html), "Pagination component is missing"
    assert ('Page 1' in html), "Pagination value is missing"
