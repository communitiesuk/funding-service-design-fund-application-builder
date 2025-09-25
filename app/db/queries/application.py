from datetime import datetime
from uuid import uuid4

from flask import current_app
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.db.models import Form, Section
from app.db.queries.round import get_round_by_id


def get_section_by_id(section_id) -> Section:
    s = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    return s


def get_form_by_id(form_id: str) -> Form:
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    return form


# CRUD operations for Section and Form
# CRUD SECTION
def insert_new_section(new_section_config):
    """
    Inserts a section object based on the provided configuration.

    Parameters:
        new_section_config (dict): A dictionary containing the configuration for the new section.
            new_section_config keys:
                - round_id (str): The ID of the round to which the section belongs.
                - name_in_apply_json (dict): The name of the section as it will be in the Application
                JSON (support multiple languages/keys).
                - template_name (str): The name of the template.
                - is_template (bool): A flag indicating whether the section is a template.
                - source_template_id (str): The ID of the source template.
                - audit_info (dict): Audit information for the section.
                - index (int): The index of the section.
            Returns:
                Section: The newly created section object.
    """
    section = Section(
        section_id=uuid4(),
        round_id=new_section_config.get("round_id", None),
        name_in_apply_json=new_section_config.get("name_in_apply_json"),
        template_name=new_section_config.get("template_name", None),
        is_template=new_section_config.get("is_template", False),
        source_template_id=new_section_config.get("source_template_id", None),
        audit_info=new_section_config.get("audit_info", {}),
        index=new_section_config.get("index"),
    )
    db.session.add(section)
    db.session.commit()
    return section


def update_section(section_id, new_section_config):
    section = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    if section:
        # Define a list of allowed keys to update
        allowed_keys = ["round_id", "name_in_apply_json", "template_name", "is_template", "audit_info", "index"]

        for key, value in new_section_config.items():
            # Update the section if the key is allowed
            if key in allowed_keys:
                setattr(section, key, value)

        db.session.commit()
    return section


def delete_section_from_round(round_id, section_id, cascade: bool = False):
    """Removes a section from the application config for a round. Uses `reorder()` on the
    round to update numbering so if there are 3 sections in a round numbered as follows:
    - 1 Round A
    - 2 Round B
    - 3 Round C

    And then round B is deleted, you get
    - 1 Round A
    - 2 Round C

    Args:
        round_id (UUID): ID of the round to remove the section from
        section_id (UUID): ID of the section to remove
        cascade (bool, optional): Whether to cascade delete forms within this section. Defaults to False.
    """
    delete_section(section_id=section_id, cascade=cascade)
    round = get_round_by_id(id=round_id)
    round.sections.reorder()
    db.session.commit()


def delete_section(section_id, cascade: bool = False):
    """Removes a section from the database. If cascade=True, will also cascade the delete
    to all forms within this section, and on down the hierarchy. This DOES NOT update
    numbering of any other sections in the round. If you want this, use
    `.delete_section_from_round()` instead.

    Args:
        section_id (_type_): section ID to delete
        cascade (bool, optional): Whether to cascade the delete down the hierarchy. Defaults to False.

    """
    section = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    if cascade:
        _delete_all_forms_in_sections(section_ids=[section_id])
    db.session.delete(section)
    db.session.commit()
    return section


def insert_form(section_id: str, url_path: str, section_index: int) -> Form:
    form = Form(
        form_id=uuid4(),
        section_id=section_id,
        section_index=section_index,
        created_at=datetime.now(),
        url_path=url_path,
    )
    try:
        db.session.add(form)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise e
    return form


def _delete_all_forms_in_sections(section_ids: list):
    stmt = delete(Form).filter(Form.section_id.in_(section_ids))
    db.session.execute(stmt)
    db.session.commit()


def delete_form_from_section(section_id, form_id):
    """Deletes a form from a section and renumbers all remaining forms accordingly.

    So for example if you have 3 sections:
    - 1 Section A
    - 2 Section B
    - 3 Section C
    Then delete section B, they are renumbered as:
    - 1 Section A
    - 2 Section C

    Args:
        section_id (_type_): Section ID to remove the form from
        form_id (_type_): Form ID of the form to remove
    """
    delete_form(form_id)
    section = get_section_by_id(section_id=section_id)
    section.forms.reorder()
    db.session.commit()


def delete_form(form_id):
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    if not form:
        raise ValueError(f"Form template with id {Form.form_id} not found")
    try:
        db.session.delete(form)
        db.session.commit()
        return form
    except Exception as e:
        db.session.rollback()
        print(f"Failed to delete form template {Form.form_id} : Error {e}")


# Section and form reordering


def swap_elements_in_list(containing_list: list, index_a: int, index_b: int) -> list:
    """Swaps the elements at the specified indices in the supplied list.
    If either index is outside the valid range, returns the list unchanged.

    Args:
        containing_list (list): List containing the elements to swap
        index_a (int): List index (0-based) of the first element to swap
        index_b (int): List index (0-based) of the second element to swap

    Returns:
        list: The updated list
    """
    if 0 <= index_a < len(containing_list) and 0 <= index_b < len(containing_list):
        containing_list[index_a], containing_list[index_b] = containing_list[index_b], containing_list[index_a]
    return containing_list


def move_section_down(round_id, section_id):
    """Moves a section one place down in the ordered list of sections in a round.
    In this case down means visually down, so the index number will increase by 1.

    Element | Section.index | Index in list
        A   |   1           |   0
        B   |   2           |   1
        C   |   3           |   2

    Then move B down, which results in C moving up

    Element | Section.index | Index in list
        A   |   1           |   0
        C   |   2           |   1
        B   |   3           |   2

    Args:
        round_id (UUID): Round ID to move this section within
        section_id (UUID): ID of the section to move down
    """
    round = get_round_by_id(round_id)
    section = get_section_by_id(section_id)
    list_index = section.index - 1  # Convert from 1-based to 0-based index
    round.sections = swap_elements_in_list(round.sections, list_index, list_index + 1)
    db.session.commit()


def move_section_up(round_id, section_id):
    """Moves a section one place up in the ordered list of sections in a round.
    In this case up means visually up, so the index number will decrease by 1.

    Args:
        round_id (UUID): Round ID to move this section within
        section_id (UUID): ID of the section to move up
    """

    round = get_round_by_id(round_id)
    section = get_section_by_id(section_id)
    list_index = section.index - 1  # Convert from 1-based to 0-based index
    round.sections = swap_elements_in_list(round.sections, list_index, list_index - 1)
    db.session.commit()


def move_form_down(section_id, form_id):
    """Moves a form one place down in the ordered list of forms in a section.
    In this case down means visually down, so the index number will increase by 1.

    Element | Form.section_index    | Index in list
        A   |   1                   |   0
        B   |   2                   |   1
        C   |   3                   |   2

    Then move B down, which results in C moving up

    Element | Form.section_index    | Index in list
        A   |   1                   |   0
        C   |   2                   |   1
        B   |   3                   |   2

    Args:
        section_id (UUID): Section ID to move this form within
        form_id (UUID): ID of the form to move down
    """
    section = get_section_by_id(section_id)
    form = get_form_by_id(form_id)
    list_index = form.section_index - 1  # Convert from 1-based to 0-based index
    section.forms = swap_elements_in_list(section.forms, list_index, list_index + 1)
    db.session.commit()


def move_form_up(section_id, form_id):
    """Moves a form one place up in the ordered list of forms in a section.
    In this case up means visually up, so the index number will decrease by 1.


    Element | Form.section_index    | Index in list
        A   |   1                   |   0
        B   |   2                   |   1
        C   |   3                   |   2

    Then move B up, which results in A moving down

    Element | Form.section_index    | Index in list
        B   |   1                   |   0
        A   |   2                   |   1
        C   |   3                   |   2

    Args:
        section_id (UUID): Section ID to move this form within
        form_id (UUID): ID of the form to move up
    """

    section = get_section_by_id(section_id)
    form = get_form_by_id(form_id)
    list_index = form.section_index - 1  # Convert from 1-based to 0-based index
    section.forms = swap_elements_in_list(section.forms, list_index, list_index - 1)
    db.session.commit()
