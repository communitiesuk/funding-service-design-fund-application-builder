import uuid
from dataclasses import dataclass
from typing import List

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON, REAL, UUID
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.types import Boolean

from app.db import db
from app.db.models import Component

BaseModel: DefaultMeta = db.Model


@dataclass
class Criteria(BaseModel):
    criteria_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    round_id = Column(
        UUID(as_uuid=True),
        ForeignKey("round.round_id"),
        nullable=True,
    )
    name = Column(String())
    weighting = Column(REAL(precision=2))
    template_name = Column("Template Name", String(), nullable=True)
    is_template = Column("is_template", Boolean, default=False, nullable=False)
    audit_info = Column("audit_info", JSON(none_as_null=True))
    subcriteria: Mapped[List["Subcriteria"]] = relationship("Subcriteria")
    index = Column(Integer())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)


@dataclass
class Subcriteria(BaseModel):
    subcriteria_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    criteria_id = Column(
        UUID(as_uuid=True),
        ForeignKey("criteria.criteria_id"),
        nullable=True,
    )
    name = Column(String())
    template_name = Column(String(), nullable=True)
    is_template = Column("is_template", Boolean, default=False, nullable=False)
    audit_info = Column("audit_info", JSON(none_as_null=True))
    themes: Mapped[List["Theme"]] = relationship("Theme")
    criteria_index = Column(Integer())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)


@dataclass
class Theme(BaseModel):
    theme_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    subcriteria_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subcriteria.subcriteria_id"),
        nullable=True,
    )
    name = Column(String())
    template_name = Column("Template Name", String(), nullable=True)
    is_template = Column("is_template", Boolean, default=False, nullable=False)
    audit_info = Column("audit_info", JSON(none_as_null=True))
    components: Mapped[List["Component"]] = relationship("Component")
    subcriteria_index = Column(Integer())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)
