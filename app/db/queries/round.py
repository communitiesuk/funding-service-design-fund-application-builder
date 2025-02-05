from flask import current_app
from sqlalchemy import String, cast, select
from sqlalchemy.orm import joinedload

from app.db import db
from app.db.models import Fund, Component, Page, Form
from app.db.models.round import Round
from app.db.queries.util import delete_all_related_objects


def add_round(round: Round) -> Round:
    db.session.add(round)
    db.session.commit()
    current_app.logger.info("Round added with round_id: '{round_id}'.", extra=dict(round_id=round.round_id))
    return round


def update_round(round: Round) -> Round:
    db.session.commit()
    current_app.logger.info("Round updated with round_id: '{round_id}'.", extra=dict(round_id=round.round_id))
    return round


def get_round_by_id(id: str) -> Round:
    round = db.session.get(Round, id)
    if not round:
        raise ValueError(f"Round with id {id} not found")
    return round


def get_round_by_short_name_and_fund_id(fund_id: str, short_name: str) -> Round:
    return db.session.query(Round).filter_by(fund_id=fund_id, short_name=short_name).first()


def get_all_rounds() -> list[Round]:
    stmt = select(Round).join(Round.fund).order_by(cast(Fund.title_json["en"], String))
    return db.session.scalars(stmt).all()


def _delete_sections_for_round(round_detail: Round):
    for section_detail in round_detail.sections:
        page_ids = [page.page_id for form in section_detail.forms for page in form.pages]
        form_ids = [form.form_id for form in section_detail.forms]
        section_ids = [section_detail.section_id]

        delete_all_related_objects(db=db, model=Component, column=Component.page_id, ids=page_ids)
        delete_all_related_objects(db=db, model=Page, column=Page.form_id, ids=form_ids)
        delete_all_related_objects(db=db, model=Form, column=Form.section_id, ids=section_ids)

        db.session.delete(section_detail)
        db.session.commit()


def delete_selected_round(round_id):
    round_detail: Round = db.session.query(Round).options(joinedload(Round.sections)).get(round_id)
    if not round_detail:
        raise ValueError(f"Round with id {round_id} not found")
    try:
        _delete_sections_for_round(round_detail)
        delete_all_related_objects(db=db, model=Round, column=Round.round_id, ids=[round_id])
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Failed to delete round {round_id} : Error {e}")
