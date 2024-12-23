import uuid
from dataclasses import dataclass
from enum import Enum
from typing import List

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, JSON, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.types import Boolean

from app.db import db

from .round import Round

BaseModel: DefaultMeta = db.Model


class FundingType(Enum):
    COMPETITIVE = "COMPETITIVE"
    UNCOMPETED = "UNCOMPETED"
    EOI = "EOI"

    def get_text_for_display(self):
        match self:
            case FundingType.COMPETITIVE:
                return "Competitive"
            case FundingType.EOI:
                return "EOI"
            case FundingType.UNCOMPETED:
                return "Uncompeted"
            case _:
                return self.value


@dataclass
class Organisation(BaseModel):
    organisation_id = Column(
        "organisation_id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column("name", db.String(100), nullable=False, unique=True)
    short_name = Column("short_name", db.String(15), nullable=False, unique=True)
    logo_uri = Column("logo_uri", db.String(100), nullable=True, unique=False)
    audit_info = Column("audit_info", JSON(none_as_null=True))
    funds: Mapped[List["Fund"]] = relationship("Fund", back_populates="owner_organisation", passive_deletes="all")


@dataclass
class Fund(BaseModel):
    fund_id = Column(
        "fund_id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name_json = Column("name_json", MutableDict.as_mutable(JSON(none_as_null=True)), nullable=False, unique=False)
    title_json = Column("title_json", MutableDict.as_mutable(JSON(none_as_null=True)), nullable=False, unique=False)
    short_name = Column("short_name", db.String(15), nullable=False, unique=True)
    description_json = Column(
        "description_json", MutableDict.as_mutable(JSON(none_as_null=True)), nullable=False, unique=False
    )
    welsh_available = Column("welsh_available", Boolean, default=False, nullable=False)
    is_template = Column("is_template", Boolean, default=False, nullable=False)
    audit_info = Column("audit_info", JSON(none_as_null=True))
    rounds: Mapped[List["Round"]] = relationship("Round")
    owner_organisation_id = Column(UUID(as_uuid=True), ForeignKey("organisation.organisation_id"), nullable=True)
    # Define the relationship to access the owning Organisation directly
    owner_organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="funds")
    funding_type = Column(ENUM(FundingType), nullable=False, unique=False)
    ggis_scheme_reference_number = Column("ggis_scheme_reference_number", db.String(255), nullable=True, unique=False)
