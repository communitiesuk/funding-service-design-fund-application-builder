from flask import current_app

from app.all_questions.metadata_utils import generate_print_data_for_sections
from app.config_generator.generate_all_questions import print_html
from app.config_generator.generate_form import build_form_json
from app.config_generator.scripts.helpers import write_config
from app.db.queries.round import get_round_by_id


def generate_all_round_html(round_id):
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
    current_app.logger.info(f"Generating HTML for round {round_id}.")
    round = get_round_by_id(round_id)
    sections_in_round = round.sections
    section_data = []
    for section in sections_in_round:
        forms = [{"name": form.runner_publish_name, "form_data": build_form_json(form)} for form in section.forms]
        section_data.append({"section_title": section.name_in_apply_json["en"], "forms": forms})

    print_data = generate_print_data_for_sections(
        section_data,
        lang="en",
    )
    html_content = print_html(print_data)
    write_config(html_content, "full_application", round.short_name, "html")
