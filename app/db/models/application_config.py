import uuid
from dataclasses import dataclass
from typing import List

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column, ForeignKey, Integer, String, inspect
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.types import Boolean

from app.db import db

BaseModel: DefaultMeta = db.Model


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

    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in inspect(self).mapper.columns}


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
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    section_index = Column(Integer())
    runner_publish_name = Column(db.String())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)
    form_json = Column(JSON(none_as_null=True), nullable=True)

    def __repr__(self):
        return f"Form({self.section_index}, {self.runner_publish_name}" + f"- {self.name_in_apply_json['en']})"

    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in inspect(self).mapper.columns}
