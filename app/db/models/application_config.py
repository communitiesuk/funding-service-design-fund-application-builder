# from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import List

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean

from app.db import db

BaseModel: DefaultMeta = db.Model


class ComponentType(Enum):
    TEXT_FIELD = "TextField"
    FREE_TEXT_FIELD = "FreeTextField"
    EMAIL_ADDRESS_FIELD = "EmailAddressField"
    TELEPHONE_NUMBER_FIELD = "TelephoneNumberField"
    UK_ADDRESS_FIELD = "UkAddressField"
    HTML = "Html"
    YES_NO_FIELD = "YesNoField"
    RADIOS_FIELD = "RadiosField"
    PARA = "Para"
    DATE_PARTS_FIELD = "DatePartsField"
    CHECKBOXES_FIELD = "CheckboxesField"
    CLIENT_SIDE_FILE_UPLOAD_FIELD = "ClientSideFileUploadField"
    WEBSITE_FIELD = "WebsiteField"


@dataclass
class Section(BaseModel):

    round_id = Column(
        UUID(as_uuid=True),
        ForeignKey("round.round_id"),
        nullable=True,  # will be null where this is a template and not linked to a round
    )
    section_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name_in_apply_json = Column(JSON(none_as_null=True), nullable=False, unique=False)
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    forms: Mapped[List["Form"]] = relationship(
        "Form", order_by="Form.section_index", collection_class=ordering_list("section_index"), passive_deletes="all"
    )
    index = Column(Integer())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"Section([{self.section_id}], {self.name_in_apply_json['en']}, Forms: {self.forms})"

    def as_dict(self, include_relationships=False):
        result = {col.name: getattr(self, col.name) for col in inspect(self).mapper.columns}
        if include_relationships & hasattr(self, "forms"):
            result["forms"] = [form.as_dict() for form in self.forms if self.forms is not None]
        return result


@dataclass
class Form(BaseModel):

    section_id = Column(
        UUID(as_uuid=True),
        ForeignKey("section.section_id"),
        nullable=True,  # will be null where this is a template and not linked to a section
    )
    form_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name_in_apply_json = Column(JSON(none_as_null=True), nullable=False, unique=False)
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    section_index = Column(Integer())
    pages: Mapped[List["Page"]] = relationship(
        "Page", order_by="Page.form_index", collection_class=ordering_list("form_index"), passive_deletes="all"
    )
    runner_publish_name = Column(db.String())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"Form({self.runner_publish_name} - {self.name_in_apply_json['en']}, Pages: {self.pages})"

    def as_dict(self, include_relationships=False):
        result = {col.name: getattr(self, col.name) for col in inspect(self).mapper.columns}
        if include_relationships & hasattr(self, "pages"):
            result["pages"] = [page.as_dict() for page in self.pages if self.pages is not None]
        return result


@dataclass
class Page(BaseModel):

    form_id = Column(
        UUID(as_uuid=True),
        ForeignKey("form.form_id"),
        nullable=True,  # will be null where this is a template and not linked to a form
    )
    page_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name_in_apply_json = Column(JSON(none_as_null=True), nullable=False, unique=False)
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    form_index = Column(Integer())
    display_path = Column(String())
    default_next_page_id = Column(UUID(as_uuid=True), ForeignKey("page.page_id"), nullable=True)
    components: Mapped[List["Component"]] = relationship(
        "Component",
        order_by="Component.page_index",
        collection_class=ordering_list("page_index"),
        passive_deletes="all",
    )
    source_template_id = Column(UUID(as_uuid=True), nullable=True)
    controller = Column(String(), nullable=True)

    def __repr__(self):
        return f"Page(/{self.display_path} - {self.name_in_apply_json['en']}, Components: {self.components})"

    def as_dict(self, include_relationships=False):
        result = {col.name: getattr(self, col.name) for col in inspect(self).mapper.columns}

        if include_relationships & hasattr(self, "components"):
            result["components"] = [component.as_dict() for component in self.components if self.components is not None]

        return result


# Ensure we can only have one template with a particular display_path value
Index("ix_template_page_name", Page.display_path, Page.form_id, unique=True, postgresql_where="Page.is_template = true")


class Lizt(BaseModel):
    list_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(String())
    title = Column(String())
    type = Column(String())
    items = Column(JSON())
    is_template = Column(Boolean, default=False, nullable=False)

    def as_dict(self):
        return {col.name: self.__getattribute__(col.name) for col in inspect(self).mapper.columns}


@dataclass
class Component(BaseModel):

    component_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    page_id = Column(
        UUID(as_uuid=True),
        ForeignKey("page.page_id"),
        nullable=True,  # will be null where this is a template and not linked to a page
    )
    theme_id = Column(
        UUID(as_uuid=True),
        ForeignKey("theme.theme_id"),
        nullable=True,  # will be null where this is a template and not linked to a theme
    )
    # TODO make these 2 json so we can do welsh?
    title = Column(String())
    hint_text = Column(String(), nullable=True)
    options = Column(JSON(none_as_null=False))
    type = Column(ENUM(ComponentType))
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    page_index = Column(Integer())
    theme_index = Column(Integer())
    conditions = Column(JSON(none_as_null=True))
    source_template_id = Column(UUID(as_uuid=True), nullable=True)
    runner_component_name = Column(
        String(), nullable=False
    )  # TODO add validation to make sure it's only letters, numbers and _
    list_id = Column(
        UUID(as_uuid=True),
        ForeignKey("list.list_id"),
        nullable=True,
    )
    list_id: Mapped[int | None] = mapped_column(ForeignKey("lizt.list_id"))
    lizt: Mapped[Lizt | None] = relationship()  # back_populates="used_by")

    def __repr__(self):
        return f"Component({self.title}, {self.type.value})"

    def as_dict(self):
        return {col.name: self.__getattribute__(col.name) for col in inspect(self).mapper.columns}

    @property
    def assessment_display_type(self):
        # TODO extend this to account for what's in self.options eg. if prefix==£, return 'currency'
        return {
            "numberfield": "integer",
            "textfield": "text",
            "yesnofield": "text",
            "freetextfield": "free_text",
            "checkboxesfield": "list",
            "multiinputfield": "table",
            "clientsidefileuploadfield": "s3bucketPath",
            "radiosfield": "text",
            "emailaddressfield": "text",
            "telephonenumberfield": "text",
            "ukaddressfield": "address",
        }.get(self.type.value.casefold())
