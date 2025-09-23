from uuid import uuid4

from app.db import db
from app.db.models import Round, Section
from app.db.queries.application import insert_new_section_form


def clone_single_round(round_id, new_fund_id, new_short_name) -> Round:
    round_to_clone = db.session.query(Round).where(Round.round_id == round_id).one_or_none()
    cloned_round = Round(**round_to_clone.as_dict())
    cloned_round.fund_id = new_fund_id
    cloned_round.short_name = new_short_name
    cloned_round.title_json["en"] = "Copy of " + cloned_round.title_json.get("en")
    cloned_round.title_json["cy"] = (
        "Copi o " + cloned_round.title_json.get("cy") if cloned_round.title_json.get("cy", None) else ""
    )
    cloned_round.round_id = uuid4()
    cloned_round.is_template = False
    cloned_round.source_template_id = round_to_clone.round_id
    cloned_round.template_name = None
    cloned_round.sections = []
    cloned_round.section_base_path = None

    db.session.add(cloned_round)
    db.session.commit()

    for section in round_to_clone.sections:
        clone_single_section(section.section_id, cloned_round.round_id)

    return cloned_round


def clone_single_section(section_id: str, new_round_id=None) -> Section:
    section_to_clone: Section = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    cloned_section = Section(**section_to_clone.as_dict())
    cloned_section.round_id = new_round_id
    cloned_section.section_id = uuid4()
    cloned_section.is_template = False
    cloned_section.source_template_id = section_to_clone.section_id
    cloned_section.template_name = None

    db.session.add(cloned_section)
    db.session.commit()

    for form in section_to_clone.forms:
        insert_new_section_form(
            section_id=section_to_clone.section_id, url_path=form.url_path, section_index=form.section_index
        )

    return cloned_section
