import uuid
from dataclasses import dataclass

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean

from app.db import db
from app.db.models import Criteria
from app.db.models import Section

BaseModel: DefaultMeta = db.Model


@dataclass
class Round(BaseModel):
    __table_args__ = (UniqueConstraint("fund_id", "short_name"),)
    round_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    fund_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fund.fund_id"),
        nullable=False,
    )
    title_json = Column(MutableDict.as_mutable(JSON(none_as_null=True)), nullable=False, unique=False)
    short_name = Column(db.String(), nullable=False, unique=False)
    opens = Column(DateTime())
    deadline = Column(DateTime())
    assessment_start = Column(DateTime())
    reminder_date = Column(DateTime())
    assessment_deadline = Column(DateTime())
    prospectus_link = Column(db.String(), nullable=False, unique=False)
    privacy_notice_link = Column(db.String(), nullable=False, unique=False)
    audit_info = Column(JSON(none_as_null=True))
    is_template = Column(Boolean, default=False, nullable=False)
    source_template_id = Column(UUID(as_uuid=True), nullable=True)
    template_name = Column(String(), nullable=True)
    sections: Mapped[list["Section"]] = relationship(
        "Section",
        order_by="Section.index",
        collection_class=ordering_list("index", count_from=1),
        passive_deletes="all",
    )
    criteria: Mapped[list["Criteria"]] = relationship("Criteria")
    # several other fields to add
    application_reminder_sent = Column(Boolean, default=False, nullable=False)
    contact_us_banner_json = Column(MutableDict.as_mutable(JSON(none_as_null=True)), nullable=True, unique=False)
    reference_contact_page_over_email = Column(Boolean, default=False, nullable=False)
    contact_email = Column(db.String(), nullable=True, unique=False)
    contact_phone = Column(db.String(), nullable=True, unique=False)
    contact_textphone = Column(db.String(), nullable=True, unique=False)
    support_times = Column(db.String(), nullable=False, unique=False)
    support_days = Column(db.String(), nullable=False, unique=False)
    instructions_json = Column(MutableDict.as_mutable(JSON(none_as_null=True)), nullable=True, unique=False)
    feedback_link = Column(db.String(), unique=False)
    project_name_field_id = Column(db.String(), unique=False, nullable=False)
    application_guidance_json = Column(MutableDict.as_mutable(JSON(none_as_null=True)), nullable=True, unique=False)
    guidance_url = Column(db.String(), nullable=True, unique=False)
    all_uploaded_documents_section_available = Column(Boolean, default=False, nullable=False)
    application_fields_download_available = Column(Boolean, default=False, nullable=False)
    display_logo_on_pdf_exports = Column(Boolean, default=False, nullable=False)
    mark_as_complete_enabled = Column(Boolean, default=False, nullable=False)
    is_expression_of_interest = Column(Boolean, default=False, nullable=False)
    feedback_survey_config = Column(JSON(none_as_null=True), nullable=True, unique=False)
    eligibility_config = Column(MutableDict.as_mutable(JSON(none_as_null=True)), nullable=True, unique=False)
    eoi_decision_schema = Column(JSON(none_as_null=True), nullable=True, unique=False)

    def __repr__(self):
        return f"Round({self.short_name} - {self.title_json['en']}, Sections: {self.sections})"

    def as_dict(self):
        return {col.name: self.__getattribute__(col.name) for col in inspect(self).mapper.columns}
