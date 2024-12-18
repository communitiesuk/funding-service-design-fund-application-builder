from app.blueprints.self_serve.data.not_a_db import COMPONENTS, FORMS, LISTS, PAGES, SECTIONS

saved_responses = []
saved_sections = {}


def save_form(form_config):
    FORMS.append(form_config)


def get_saved_forms():
    return FORMS


def get_all_sections():
    return SECTIONS


# def clear_saved_forms():
#     saved_forms = {}
#     return


def save_response(form_dict: dict) -> dict:
    saved_responses.append(form_dict)
    return form_dict


def get_responses() -> list:
    return saved_responses


def clear_all_responses():
    saved_responses.clear()


def get_all_components() -> list:
    return COMPONENTS


def get_component_by_name(component_name: str) -> dict:
    return next((c for c in COMPONENTS if c["id"] == component_name), None)


def get_all_pages() -> list:
    return PAGES


def get_pages_to_display_in_builder() -> list:
    return [p for p in PAGES if p["show_in_builder"] is True]


def get_page_by_id(id: str) -> dict:
    return next((p for p in PAGES if p["id"] == id), None)


def save_page(page: dict):
    PAGES.append(page)


def get_list_by_id(id: str) -> dict:
    return LISTS.get(id, None)


# TODO Implement front end journey that can use the section/form/page/component CRUD operations
# from app.db.queries.application import insert_new_section
# from app.db.queries.application import insert_new_form
# from app.db.queries.application import insert_new_page
# from app.db.queries.application import insert_new_component


def save_template_component(component: dict):
    """
    TODO:
    Save a template component to the database
        Parameters:
            component: dict    The component to save to the database as a template
        Returns:
            dict           The saved component

    component_config = {
        "page_id": component.get("page_id"),
        "theme_id": component.get("theme_id"),
        "title": component.get("title"),
        "hint_text": component.get("hint"),
        "options": component.get("options"),
        "type": component.get("question_type"),
        "template_name": component.get("template_name"),
        "is_template": True,
        "audit_info": component.get("audit_info"),
        "page_index": component.get("page_index"),
        "theme_index": component.get("theme_index"),
        "conditions": component.get("conditions"),
        "runner_component_name": component.get("runner_component_name"),
        "list_id": component.get("list_id"),
    }

    return insert_new_component(component_config)
    """

    #  temp in memory solution
    COMPONENTS.append(
        {
            "json_snippet": {
                "options": {},
                "type": component["question_type"],
                "title": component["title"],
                "hint": component["hint"],
            },
            "id": component["id"],
            "builder_display_name": component["builder_display_name"],
        }
    )


def save_template_page(page: dict):
    """
    TODO:
    Save a template page to the database
        Parameters:
            page: dict    The page to save to the database as a template
        Returns:
            dict           The saved page

    page_config = {
        "form_id": page.get("form_id"),
        "name_in_apply_json": {
            "en": page.get("form_display_name"),
        },
        "template_name": page.get("builder_display_name"),
        "is_template": True,
        "audit_info": page.get("audit_info"),
        "form_index": page.get("form_index"),
        "display_path": page.get("display_path"),
        "controller": page.get("controller"),
    }

    return insert_new_page(page_config)
    """

    # Temp in memory solution
    PAGES.append(page)


def save_template_form(form: dict):
    """
    TODO:
    Save a template form to the database
        Parameters:
            form: dict    The form to save to the database as a template
        Returns:
            dict           The saved form
    form_config = {
        "name_in_apply_json": {
            "en": form.get("form_title"),
        },
        "is_template": True,
        "template_name": form.get("builder_display_name"),
        "audit_info": form.get("audit_info"),
        "section_id": form.get("section_id"),
        "section_index": form.get("section_index"),
        "runner_publish_name": None # This is a template
    }

    insert_new_form(form_config)
    """

    # Temp in memory solution
    FORMS.append(form)


def save_template_section(section: dict):
    """
    TODO:
    Save a template section to the database
        Parameters:
          section: dict    The section to save to the database as a template
        Returns:
            dict           The saved section

    section_config = {
        "name_in_apply_json": {
            "en": section.get("section_display_name"),
        },
        "is_template": True,  # Assuming this remains a constant value
        "template_name": section.get("builder_display_name"),
        "description": section.get("description"),
        "audit_info": section.get("audit_info"),
    }

    return insert_new_section(section_config)
    """

    # Temp in memory solution
    SECTIONS.append(section)
