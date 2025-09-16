from flask import current_app

from app.all_questions.metadata_utils import generate_print_data_for_sections
from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_id
from app.export_config.generate_all_questions import generate_html
from app.export_config.helpers import write_config
from app.shared.form_store_api import FormStoreAPIService

frontend_html_prefix = """
{% extends "apply/base.html" %}
{%- from 'govuk_frontend_jinja/components/inset-text/macro.html' import govukInsetText -%}
{%- from "govuk_frontend_jinja/components/button/macro.html" import govukButton -%}

{% from "apply/partials/file-formats.html" import file_formats %}
{% set pageHeading %}{% trans %}Full list of application questions{% endtrans %}{% endset %}
{% block content %}
<div class="govuk-grid-row">
    <div class="govuk-grid-column-two-thirds">
        <span class="govuk-caption-l">{% trans %}{{ fund_title }}{% endtrans %}&nbsp;
        {% trans %}{{ round_title }}{% endtrans %}
        </span>
        <h1 class="govuk-heading-xl">{{ pageHeading }}</h1>
"""
frontend_html_suffix = """
    </div>
</div>
{% endblock content %}
"""


def generate_all_round_html(round_id, base_output_dir=None):
    """
    Generates an HTML representation for a specific funding round.

    This function creates an HTML document that represents all the sections and forms
    associated with a given funding round. It retrieves the round and its related fund
    information, iterates through each section of the round to collect form data, and
    then generates HTML content based on this data.

    Args:
        round_id (str): The unique identifier for the funding round.

    The process involves:
    1. Fetching the round details using its ID.
    2. Collecting data for each section and its forms within the round.
    3. Generating print data for the sections.
    4. Converting the print data into HTML content.
    5. Writing the HTML content to a file named 'html_full' within a directory
       corresponding to the round's short name.

    The generated HTML is intended to provide a comprehensive overview of the round,
    including details of each section and form, for printing or web display purposes.
    """
    if not round_id:
        raise ValueError("Round ID is required to generate HTML.")
    current_app.logger.info("Generating HTML for round {round_id}", extra=dict(round_id=round_id))
    api_service = FormStoreAPIService()
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    sections_in_round = round.sections
    section_data = []
    for section in sections_in_round:
        forms = []
        for form in section.forms:
            configuration = api_service.get_published_form(form.form_name)
            forms.append({"name": form.form_name, "form_data": configuration})
        section_data.append({"section_title": section.name_in_apply_json["en"], "forms": forms})

    print_data = generate_print_data_for_sections(
        section_data,
        lang="en",
    )
    html_content = frontend_html_prefix
    html_content += generate_html(print_data)
    html_content += frontend_html_suffix
    write_config(
        html_content,
        f"{fund.short_name.casefold()}_{round.short_name.casefold()}",
        round.short_name,
        "html",
        base_output_dir,
    )
