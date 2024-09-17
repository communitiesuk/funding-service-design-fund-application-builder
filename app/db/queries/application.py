from uuid import uuid4

from app.db import db
from app.db.models import Component
from app.db.models import Form
from app.db.models import Lizt
from app.db.models import Page
from app.db.models import Section
from app.db.models.round import Round


def get_all_template_sections() -> list[Section]:
    return db.session.query(Section).where(Section.is_template == True).all()  # noqa:E712


def get_section_by_id(section_id) -> Section:
    s = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    return s


def get_all_template_forms() -> list[Form]:
    return db.session.query(Form).where(Form.is_template == True).all()  # noqa:E712


def get_form_for_component(component: Component) -> Form:
    page_id = component.page_id
    page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    form = db.session.query(Form).where(Form.form_id == page.form_id).one_or_none()
    return form


def get_template_page_by_display_path(display_path: str) -> Page:
    page = (
        db.session.query(Page)
        .where(Page.display_path == display_path)
        .where(Page.is_template == True)  # noqa:E712
        .one_or_none()
    )
    return page


def get_form_by_id(form_id: str) -> Form:
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    return form


def get_component_by_id(component_id: str) -> Component:
    component = db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    return component


def get_list_by_id(list_id: str) -> Lizt:
    lizt = db.session.query(Lizt).where(Lizt.list_id == list_id).one_or_none()
    return lizt


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
        cloned_form = _initiate_cloned_form(form_to_clone, clone.section_id)
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
    cloned_round.round_id = uuid4()
    cloned_round.is_template = False
    cloned_round.source_template_id = round_to_clone.round_id
    cloned_round.template_name = None
    cloned_round.sections = []

    db.session.add(cloned_round)
    db.session.commit()

    for section in round_to_clone.sections:
        clone_single_section(section.section_id, cloned_round.round_id)

    return cloned_round


# CRUD operations for Section, Form, Page, and Component
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


def delete_section(section_id):
    section = db.session.query(Section).where(Section.section_id == section_id).one_or_none()
    db.session.delete(section)
    db.session.commit()
    return section


# CRUD FORM
def insert_new_form(new_form_config):
    """
    Inserts a form object based on the provided configuration.

    Parameters:
        new_form_config (dict): A dictionary containing the configuration for the new form.
            new_form_config keys:
                - section_id (str): The ID of the section to which the form belongs.
                - name_in_apply_json (dict): The name of the form as it will be in the Application
                JSON (support multiple languages/keys).
                - is_template (bool): A flag indicating whether the form is a template.
                - template_name (str): The name of the template.
                - source_template_id (str): The ID of the source template.
                - audit_info (dict): Audit information for the form.
                - section_index (int): The index of the form within the section.
                - runner_publish_name (bool): The path of the form in the form runner (kebab case).
    Returns:
        Form: The newly created form object.
    """

    form = Form(
        form_id=uuid4(),
        section_id=new_form_config.get("section_id", None),
        name_in_apply_json=new_form_config.get("name_in_apply_json"),
        is_template=new_form_config.get("is_template", False),
        template_name=new_form_config.get("template_name", None),
        source_template_id=new_form_config.get("source_template_id", None),
        audit_info=new_form_config.get("audit_info", {}),
        section_index=new_form_config.get("section_index"),
        runner_publish_name=new_form_config.get("runner_publish_name", None),
    )
    db.session.add(form)
    db.session.commit()
    return form


def update_form(form_id, new_form_config):
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    if form:
        # Define a list of allowed keys to update
        allowed_keys = [
            "section_id",
            "name_in_apply_json",
            "template_name",
            "is_template",
            "audit_info",
            "section_index",
            "runner_publish_name",
        ]

        # Iterate over the new_form_config dictionary
        for key, value in new_form_config.items():
            # Update the form if the key is allowed
            if key in allowed_keys:
                setattr(form, key, value)

        db.session.commit()
    return form


def delete_form(form_id):
    form = db.session.query(Form).where(Form.form_id == form_id).one_or_none()
    db.session.delete(form)
    db.session.commit()
    return form


# CRUD PAGE
def insert_new_page(new_page_config):
    """
    Inserts a page object based on the provided configuration.

    Parameters:
        new_page_config (dict): A dictionary containing the configuration for the new page.
            new_page_config keys:
                - form_id (str): The ID of the form to which the page belongs.
                - name_in_apply_json (str): The name of the page as it will be in the Application JSON.
                - template_name (str): The name of the template.
                - is_template (bool): A flag indicating whether the page is a template.
                - source_template_id (str): The ID of the source template.
                - audit_info (dict): Audit information for the page.
                - form_index (int): The index of the page within the form.
                - display_path (str): The form runner display path of the page (kebab case).
                - controller (str): The form runner controller path for the page (e.g. './pages/summary.js').
                Returns:
            Page: The newly created page object.
    """
    page = Page(
        page_id=uuid4(),
        form_id=new_page_config.get("form_id", None),
        name_in_apply_json=new_page_config.get("name_in_apply_json"),
        template_name=new_page_config.get("template_name", None),
        is_template=new_page_config.get("is_template", False),
        source_template_id=new_page_config.get("source_template_id", None),
        audit_info=new_page_config.get("audit_info", {}),
        form_index=new_page_config.get("form_index"),
        display_path=new_page_config.get("display_path"),
        controller=new_page_config.get("controller", None),
    )
    db.session.add(page)
    db.session.commit()
    return page


def update_page(page_id, new_page_config):
    page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    if page:
        # Define a list of allowed keys to update
        allowed_keys = [
            "form_id",
            "name_in_apply_json",
            "template_name",
            "is_template",
            "audit_info",
            "form_index",
            "display_path",
            "controller",
        ]

        for key, value in new_page_config.items():
            # Update the page if the key is allowed
            if key in allowed_keys:
                setattr(page, key, value)

        db.session.commit()
    return page


def delete_page(page_id):
    page = db.session.query(Page).where(Page.page_id == page_id).one_or_none()
    db.session.delete(page)
    db.session.commit()
    return page


# CRUD COMPONENT
def insert_new_component(new_component_config: dict):
    """
    Inserts a component object based on the provided configuration.

    Parameters:
        new_component_config (dict): A dictionary containing the configuration for the new component.
            new_component_config keys:
                - page_id (str): The ID of the page to which the component belongs.
                - theme_id (str): The ID of the theme to which the component belongs.
                - title (str): The title of the component.
                - hint_text (str): The hint text for the component.
                - options (dict): The options such as classes, prefix etc
                - type (str): The type of the component.
                - template_name (str): The name of the template.
                - is_template (bool): A flag indicating whether the component is a template.
                - source_template_id (str): The ID of the source template.
                - audit_info (dict): Audit information for the component.
                - page_index (int): The index of the component within the page.
                - theme_index (int): The index of the component within the theme.
                - conditions (dict): The conditions such as potential routes based on the
                components value (can specify page path).
                - runner_component_name (str): The name of the runner component.
                - list_id (str): The ID of the list to which the component belongs.
            Returns:
                Component: The newly created component object.
    """
    # Instantiate the Component object with the provided and default values
    component = Component(
        component_id=uuid4(),
        page_id=new_component_config.get("page_id", None),
        theme_id=new_component_config.get("theme_id", None),
        title=new_component_config.get("title"),
        hint_text=new_component_config.get("hint_text"),
        options=new_component_config.get("options", {}),
        type=new_component_config.get("type"),
        is_template=new_component_config.get("is_template", False),
        template_name=new_component_config.get("template_name", None),
        source_template_id=new_component_config.get("source_template_id", None),
        audit_info=new_component_config.get("audit_info", {}),
        page_index=new_component_config.get("page_index"),
        theme_index=new_component_config.get("theme_index"),
        conditions=new_component_config.get("conditions", []),
        runner_component_name=new_component_config.get("runner_component_name"),
        list_id=new_component_config.get("list_id", None),
    )

    # Add the component to the session and commit
    db.session.add(component)
    db.session.commit()

    # Return the created component object or its ID based on your requirements
    return component


def update_component(component_id, new_component_config):
    component = db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    if component:
        # Define a list of allowed keys to update to prevent updating unintended fields
        allowed_keys = [
            "page_id",
            "theme_id",
            "title",
            "hint_text",
            "options",
            "type",
            "template_name",
            "is_template",
            "audit_info",
            "page_index",
            "theme_index",
            "conditions",
            "runner_component_name",
            "list_id",
        ]

        for key, value in new_component_config.items():
            # Update the component if the key is allowed
            if key in allowed_keys:
                setattr(component, key, value)

        db.session.commit()
    return component


def delete_component(component_id):
    component = db.session.query(Component).where(Component.component_id == component_id).one_or_none()
    db.session.delete(component)
    db.session.commit()
    return component
