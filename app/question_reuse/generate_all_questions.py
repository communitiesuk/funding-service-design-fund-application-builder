from airium import Airium  # noqa: E402


# Initialise Airium html printer
air = Airium()

# Define start and end html
BOILERPLATE_START = """
{% extends "base.html" %}
{%- from 'govuk_frontend_jinja/components/inset-text/macro.html' import govukInsetText -%}
{%- from "govuk_frontend_jinja/components/button/macro.html" import govukButton -%}

{% from "partials/file-formats.html" import file_formats %}
{% set pageHeading %}{% trans %}Full list of application questions{% endtrans %}{% endset %}
{% block content %}
<div class="govuk-grid-row">
    <div class="govuk-grid-column-two-thirds">
        <span class="govuk-caption-l">{% trans %}{{fund_title}}{% endtrans %} {% trans %}{{round_title}}{% endtrans %}
        </span>
        <h1 class="govuk-heading-xl">{{pageHeading}}</h1>
"""

BOILERPLATE_END = """
    </div>
</div>
{% endblock %}
"""


def print_html_toc(air: Airium, sections: dict):
    """Prints a table of contents for the supplied sections to the supplied `Airium` instance

    Args:
        air (Airium): Instance to write html to
        sections (dict): Sections for this TOC
    """
    with air.h2(klass="govuk-heading-m "):
        air("Table of contents")
    with air.ol(klass="govuk-list govuk-list--number"):
        for anchor, details in sections.items():
            with air.li():
                with air.a(klass="govuk-link", href=f"#{anchor}"):
                    air(details["title_text"])


def print_components(air: Airium, components: list):
    """Prints the components within a page

    Args:
        air (Airium): Instance to print html
        components (list): List of components to print
    """
    for c in components:
        # Print the title
        if not c["hide_title"] and c["title"] is not None:
            with air.p(klass="govuk-body"):
                air(f"{c['title']}")

        for t in c["text"]:
            # Print lists as <ul> bullet lists
            if isinstance(t, list):
                with air.ul(klass="govuk-list govuk-list--bullet"):
                    for bullet in t:
                        with air.li(klass=""):
                            air(bullet)
            else:
                # Just print the text
                with air.p(klass="govuk-body"):
                    air(t)


def print_html(sections: dict) -> str:
    """Prints the html for the supplied sections

    Args:
        sections (dict): All sections to print, as generated by `metadata_utils.generate_print_data_for_sections`

    Returns:
        str: HTML string
    """
    air = Airium()
    with air.div(klass="govuk-!-margin-bottom-8"):
        # Print Table of Contents
        print_html_toc(air, sections)
        idx_section = 1

        for anchor, details in sections.items():
            if anchor == "assessment_display_info":
                continue
            air.hr(klass="govuk-section-break govuk-section-break--l govuk-section-break--visible")

            # Print each section header, with anchor
            with air.h2(klass="govuk-heading-l", id=anchor):
                air(f"{idx_section}. {details['title_text']}")

            form_print_data = details["form_print_data"]
            # Sort in order of numbered headings
            for heading in sorted(
                form_print_data,
                key=lambda item: str((form_print_data[item])["heading_number"]),
            ):
                header_info = form_print_data[heading]
                # Print header for this form
                if header_info["is_form_heading"]:
                    with air.h3(klass="govuk-heading-m"):
                        air(f"{header_info['heading_number']}. {header_info['title']}")

                else:
                    # Print header for this form page
                    with air.h4(klass="govuk-heading-s"):
                        air(f"{header_info['heading_number']}. {header_info['title']}")

                # Print components within this form
                print_components(air, header_info["components"])

            idx_section += 1

    # Concatenate start html, generated html and end html to one string and return
    # html = f"{BOILERPLATE_START}{str(air)}{BOILERPLATE_END}"
    return str(air)
    print(html)
    return html
