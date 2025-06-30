from uuid import UUID, uuid4

from app.db import db
from app.db.models import Component, Condition, Form, Lizt, Page, PageCondition, Round, Section


def _initiate_cloned_lizt(to_clone: Lizt) -> Lizt:
    clone = Lizt(**to_clone.as_dict())
    clone.list_id = uuid4()
    clone.is_template = False
    return clone


def _initiate_cloned_component(to_clone: Component, new_page_id=None, new_theme_id=None):
    clone = Component(**to_clone.as_dict())

    clone.component_id = uuid4()
    clone.page_id = new_page_id
    clone.theme_id = new_theme_id
    clone.is_template = False
    clone.source_template_id = to_clone.component_id
    clone.template_name = None

    if to_clone.children_components:
        child_list = []
        for child_component in to_clone.children_components:
            clone_child = Component(**child_component.as_dict())
            clone_child.component_id = uuid4()
            clone_child.parent_component = clone
            clone_child.parent_component_id = clone.component_id
            clone_child.theme_id = new_theme_id
            clone_child.is_template = False
            clone_child.source_template_id = child_component.component_id
            clone_child.template_name = None
            child_list.append(clone_child)
        clone.children_components = child_list

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


def _initiate_condition_clone(clonned: Page, to_clone: Page, form_id: UUID):
    cloned_conditions = []
    for clone_to_condition in to_clone.conditions:
        clone_condition = Condition(**clone_to_condition.as_dict())
        clone_condition.condition_id = uuid4()
        clone_condition.is_template = False
        clone_condition.form_id = form_id
        if clone_to_condition.page_conditions:
            for page_condition in clone_to_condition.page_conditions:
                clone_page_condition = PageCondition(
                    page_condition_id=uuid4(),
                    condition_id=clone_condition.condition_id,
                    page_id=clonned.page_id,
                    destination_page_path=page_condition.destination_page_path,
                    is_template=False,
                )
                clone_condition.page_conditions.append(clone_page_condition)
        clonned.conditions.append(clone_condition)
        cloned_conditions.append(clone_condition)
    return cloned_conditions


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
    cloned_lizts = []
    # loop through forms in this section and clone each one
    for form_to_clone in section_to_clone.forms:
        cloned_form = _initiate_cloned_form(form_to_clone, clone.section_id, section_index=form_to_clone.section_index)
        # loop through pages in this section and clone each one
        for page_to_clone in form_to_clone.pages:
            cloned_page = _initiate_cloned_page(page_to_clone, new_form_id=cloned_form.form_id)
            cloned_pages.append(cloned_page)
            # clone the components and lizts for component on this page
            cloned_component_list_for_page, cloned_lizts_for_page = _initiate_cloned_components_for_page(
                page_to_clone.components, cloned_page.page_id
            )
            cloned_components.extend(cloned_component_list_for_page)
            cloned_lizts.extend(cloned_lizts_for_page)

        cloned_forms.append(cloned_form)

    db.session.add_all([clone, *cloned_forms, *cloned_pages, *cloned_components, *cloned_lizts])
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
    cloned_conditions = []
    cloned_components = []
    cloned_lizts = []
    for page_to_clone in form_to_clone.pages:
        cloned_page = _initiate_cloned_page(page_to_clone, new_form_id=clone.form_id)
        cloned_conditions = cloned_conditions + _initiate_condition_clone(cloned_page, page_to_clone, clone.form_id)
        cloned_pages.append(cloned_page)
        cloned_component_list_for_page, cloned_lizt_per_page = _initiate_cloned_components_for_page(
            page_to_clone.components, cloned_page.page_id
        )
        cloned_components.extend(cloned_component_list_for_page)
        cloned_lizts.extend(cloned_lizt_per_page)
    db.session.add_all([clone, *cloned_pages, *cloned_components, *cloned_lizts, *cloned_conditions])
    cloned_pages = _fix_cloned_default_pages(cloned_pages)
    db.session.commit()

    return clone


def _initiate_cloned_components_for_page(
    components_to_clone: list[Component], new_page_id: str = None, new_theme_id: str = None
):
    cloned_components = []
    cloned_lizts = []
    for component_to_clone in components_to_clone:
        cloned_component = _initiate_cloned_component(
            component_to_clone, new_page_id=new_page_id, new_theme_id=None
        )  # TODO how should themes work when cloning?
        if component_to_clone.list_id:
            # clone lizt if component has a lizt and map it cloned component
            cloned_lizt = _initiate_cloned_lizt(component_to_clone.lizt)
            cloned_component.list_id = cloned_lizt.list_id
            cloned_lizts.append(cloned_lizt)
        cloned_components.append(cloned_component)
    return cloned_components, cloned_lizts


def clone_single_page(page_id: str, new_form_id=None) -> Page:
    page_to_clone: Page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    clone = _initiate_cloned_page(page_to_clone, new_form_id)

    cloned_components, cloned_lizts = _initiate_cloned_components_for_page(
        page_to_clone.components, new_page_id=clone.page_id
    )
    db.session.add_all([clone, *cloned_components, *cloned_lizts])
    db.session.commit()

    return clone


def clone_single_component(component_id: str, new_page_id=None, new_theme_id=None) -> Component:
    component_to_clone: Component = (
        db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    )
    clone = _initiate_cloned_component(component_to_clone, new_page_id, new_theme_id)
    if component_to_clone.list_id:
        # clone lizt if component has a lizt and map it cloned component
        cloned_lizt = _initiate_cloned_lizt(component_to_clone.lizt)
        clone.list_id = cloned_lizt.list_id
        db.session.add(cloned_lizt)
        db.session.commit()

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
