from airium import Airium

# --------------------------
# Boilerplate HTML Templates
# --------------------------
BOILERPLATE_START = """
{% extends "apply/base.html" %}
{%- from 'govuk_frontend_jinja/components/inset-text/macro.html' import govukInsetText -%}
{%- from "govuk_frontend_jinja/components/button/macro.html" import govukButton -%}

{% from "apply/partials/file-formats.html" import file_formats %}
{% set pageHeading %}{% trans %}Full list of application questions{% endtrans %}{% endset %}
{% block content %}
<div class="govuk-grid-row">
    <div class="govuk-grid-column-two-thirds">
        <span class="govuk-caption-l">{% trans %}{{fund_title}}{% endtrans %} {% trans %}{{round_title}}{% endtrans %}</span>
        <h1 class="govuk-heading-xl">{{pageHeading}}</h1>
"""

BOILERPLATE_END = """
    </div>
</div>
{% endblock %}
"""


# --------------------------
# Table of Contents Section
# --------------------------
def generate_table_of_contents(air, sections):
    """
    Generates a table of contents from the given sections.

    Example Output:
    <h2 class="govuk-heading-m">Table of contents</h2>
    <ol class="govuk-list govuk-list--number">
        <li><a class="govuk-link" href="#section1">Section 1</a></li>
        <li><a class="govuk-link" href="#section2">Section 2</a></li>
    </ol>
    """
    with air.h2(klass="govuk-heading-m"):
        air("Table of contents")
    with air.ol(klass="govuk-list govuk-list--number"):
        for anchor, details in sections.items():
            with air.li():
                with air.a(klass="govuk-link", href=f"#{anchor}"):
                    air(details["title_text"])


# --------------------------
# Component Rendering Section
# --------------------------
def render_components(air, components, show_field_types=False):
    """
    Renders components within a page.

    Example Output:
    <div class="govuk-body all-questions-component">
        <p class="govuk-body">Component Title [Type]</p>
        <ul class="govuk-list govuk-list--bullet">
            <li>Bullet 1</li>
            <li>Bullet 2</li>
        </ul>
        <p class="govuk-body">Some additional text.</p>
    </div>
    """
    for component in components:
        with air.div(klass="govuk-body all-questions-component"):
            title = component.get("title")
            if not component.get("hide_title") and title:
                with air.p(klass="govuk-body"):
                    air(title)
                    if show_field_types:
                        air(f" [{component['type']}]")

            for text in component.get("text", []):
                if isinstance(text, list):
                    with air.ul(klass="govuk-list govuk-list--bullet"):
                        for bullet in text:
                            with air.li():
                                air(bullet)
                else:
                    with air.p(klass="govuk-body"):
                        air(text)


# --------------------------
# Main HTML Generation Section
# --------------------------
def generate_html(sections, show_field_types=False, allow_table_of_content=True):
    """
    Generates an HTML document for the given sections.

     Example Output:
    <h2 class="govuk-heading-l" id="section1">1. Section 1 Title</h2>
    <h3 class="govuk-heading-m">1.1 Subheading</h3>
    <div class="govuk-body all-questions-component">
        <p class="govuk-body">Question Text</p>
    </div>
    """
    air = Airium()
    with air.div(klass="govuk-!-margin-bottom-8"):
        if allow_table_of_content:
            generate_table_of_contents(air, sections)

        for idx, (anchor, details) in enumerate(sections.items(), start=1):
            if anchor == "assessment_display_info":
                continue

            air.hr(klass="govuk-section-break govuk-section-break--l govuk-section-break--visible")

            with air.h2(klass="govuk-heading-l", id=anchor):
                air(f"{idx}. {details['title_text']}")

            for heading, header_info in sorted(details["form_print_data"].items(),
                                               key=lambda item: str(item[1]["heading_number"])):
                tag = "h3" if header_info["is_form_heading"] else "h4"
                heading_text = header_info["title"]

                with getattr(air, tag)(klass=f"govuk-heading-{'m' if tag == 'h3' else 's'}"):
                    air(heading_text)

                render_components(air, header_info["components"], show_field_types)

    return str(air)
