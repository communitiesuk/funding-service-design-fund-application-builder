# from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import List

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, inspect
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func
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
    MULTILINE_TEXT_FIELD = "MultilineTextField"
    NUMBER_FIELD = "NumberField"
    DATE_FIELD = "DateField"
    DATE_TIME_FIELD = "DateTimeField"
    DATE_TIME_PARTS_FIELD = "DateTimePartsField"
    SELECT_FIELD = "SelectField"
    INSET_TEXT_FIELD = "InsetText"
    DETAILS_FIELD = "Details"
    LIST_FIELD = "List"
    AUTO_COMPLETE_FIELD = "AutocompleteField"
    FILE_UPLOAD_FIELD = "FileUploadField"
    MONTH_YEAR_FIELD = "MonthYearField"
    TIME_FIELD = "TimeField"
    MULTI_INPUT_FIELD = "MultiInputField"


READ_ONLY_COMPONENTS = [
    ComponentType.HTML,
    ComponentType.PARA,
    ComponentType.INSET_TEXT_FIELD,
    ComponentType.DETAILS_FIELD,
]


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
        "Form",
        order_by="Form.section_index",
        collection_class=ordering_list("section_index", count_from=1),
        passive_deletes="all",
    )
    index = Column(Integer())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"Section({self.index}, {self.name_in_apply_json['en']} [{self.section_id}], Forms: {self.forms})"

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
    # TODO rename this to 'name in tasklist' as no longer us as the name in the apply json
    name_in_apply_json = Column(JSON(none_as_null=True), nullable=False, unique=False)
    section_index = Column(Integer())
    runner_publish_name = Column(db.String())
    form_json = Column(JSON(none_as_null=True), nullable=False, default=lambda: {})
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    url_path = Column(String(), nullable=True)  # Reference to url_path in Pre-Award database

    def __repr__(self):
        return f"Form({self.section_index}, {self.runner_publish_name}" + f"- {self.name_in_apply_json['en']})"

    def as_dict(self, include_relationships=False):
        result = {col.name: getattr(self, col.name) for col in inspect(self).mapper.columns}
        return result
