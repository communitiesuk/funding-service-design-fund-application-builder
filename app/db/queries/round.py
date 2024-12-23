from flask import current_app
from sqlalchemy import select

from app.db import db
from app.db.models.round import Round


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


def get_all_rounds() -> list:
    stmt = select(Round).order_by(Round.short_name)
    return db.session.scalars(stmt).all()
