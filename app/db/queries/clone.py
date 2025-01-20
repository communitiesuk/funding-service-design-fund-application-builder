from uuid import uuid4

from app.db import db
from app.db.models import Component, Form, Page, Round, Section


def _initiate_cloned_component(to_clone: Component, new_page_id=None, new_theme_id=None):
    clone = Component(**to_clone.as_dict())

    clone.component_id = uuid4()
    clone.page_id = new_page_id
    clone.theme_id = new_theme_id
    clone.is_template = False
    clone.source_template_id = to_clone.component_id
    clone.template_name = None
    return clone


def _initiate_cloned_page(to_clone: Page, new_form_id=None):
    clone = Page(**to_clone.as_dict())
    clone.page_id = uuid4()
    clone.form_id = new_form_id
    clone.is_template = False
    clone.source_template_id = to_clone.page_id
    clone.template_name = None
    clone.components = []
    return clone


def _initiate_cloned_form(to_clone: Form, new_section_id: str, section_index=0) -> Form:
    clone = Form(**to_clone.as_dict())
    clone.form_id = uuid4()
    clone.section_id = new_section_id
    clone.is_template = False
    clone.source_template_id = to_clone.form_id
    clone.template_name = None
    clone.pages = []
    clone.section_index = section_index
    return clone


def _initiate_cloned_section(to_clone: Section, new_round_id: str) -> Form:
    clone = Section(**to_clone.as_dict())
    clone.round_id = new_round_id
    clone.section_id = uuid4()
    clone.is_template = False
    clone.source_template_id = to_clone.section_id
    clone.template_name = None
    clone.pages = []
    return clone


def clone_single_section(section_id: str, new_round_id=None) -> Section:
    section_to_clone: Section = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    clone = _initiate_cloned_section(section_to_clone, new_round_id)

    cloned_forms = []
    cloned_pages = []
    cloned_components = []
    # loop through forms in this section and clone each one
    for form_to_clone in section_to_clone.forms:
        cloned_form = _initiate_cloned_form(form_to_clone, clone.section_id, section_index=form_to_clone.section_index)
        # loop through pages in this section and clone each one
        for page_to_clone in form_to_clone.pages:
            cloned_page = _initiate_cloned_page(page_to_clone, new_form_id=cloned_form.form_id)
            cloned_pages.append(cloned_page)
            # clone the components on this page
            cloned_components.extend(
                _initiate_cloned_components_for_page(page_to_clone.components, cloned_page.page_id)
            )

        cloned_forms.append(cloned_form)

    db.session.add_all([clone, *cloned_forms, *cloned_pages, *cloned_components])
    cloned_pages = _fix_cloned_default_pages(cloned_pages)
    db.session.commit()

    return clone


def _fix_cloned_default_pages(cloned_pages: list[Page]):
    # Go through each page
    # Get the page ID of the default next page (this will be a template page)
    # Find the cloned page that was created from that template
    # Get that cloned page's ID
    # Update this default_next_page to point to the cloned page

    for clone in cloned_pages:
        if clone.default_next_page_id:
            template_id = clone.default_next_page_id
            concrete_next_page = next(p for p in cloned_pages if p.source_template_id == template_id)
            clone.default_next_page_id = concrete_next_page.page_id

    return cloned_pages


def clone_single_form(form_id: str, new_section_id=None, section_index=0) -> Form:
    form_to_clone: Form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    clone = _initiate_cloned_form(form_to_clone, new_section_id, section_index=section_index)

    cloned_pages = []
    cloned_components = []
    for page_to_clone in form_to_clone.pages:
        cloned_page = _initiate_cloned_page(page_to_clone, new_form_id=clone.form_id)
        cloned_pages.append(cloned_page)
        cloned_components.extend(_initiate_cloned_components_for_page(page_to_clone.components, cloned_page.page_id))
    db.session.add_all([clone, *cloned_pages, *cloned_components])
    cloned_pages = _fix_cloned_default_pages(cloned_pages)
    db.session.commit()

    return clone


def _initiate_cloned_components_for_page(
    components_to_clone: list[Component], new_page_id: str = None, new_theme_id: str = None
):
    cloned_components = []
    for component_to_clone in components_to_clone:
        cloned_component = _initiate_cloned_component(
            component_to_clone, new_page_id=new_page_id, new_theme_id=None
        )  # TODO how should themes work when cloning?
        cloned_components.append(cloned_component)
    return cloned_components


def clone_single_page(page_id: str, new_form_id=None) -> Page:
    page_to_clone: Page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    clone = _initiate_cloned_page(page_to_clone, new_form_id)

    cloned_components = _initiate_cloned_components_for_page(page_to_clone.components, new_page_id=clone.page_id)
    db.session.add_all([clone, *cloned_components])
    db.session.commit()

    return clone


def clone_single_component(component_id: str, new_page_id=None, new_theme_id=None) -> Component:
    component_to_clone: Component = (
        db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    )
    clone = _initiate_cloned_component(component_to_clone, new_page_id, new_theme_id)

    db.session.add(clone)
    db.session.commit()

    return clone


# TODO do we need this?
def clone_multiple_components(component_ids: list[str], new_page_id=None, new_theme_id=None) -> list[Component]:
    components_to_clone: list[Component] = (
        db.session.query(Component).filter(Component.component_id.in_(component_ids)).all()
    )
    clones = [
        _initiate_cloned_component(to_clone=to_clone, new_page_id=new_page_id, new_theme_id=new_theme_id)
        for to_clone in components_to_clone
    ]
    db.session.add_all(clones)
    db.session.commit()

    return clones


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
