from sqlalchemy import select

from app.db import db
from app.db.models.round import Round
from flask import current_app


def add_round(round: Round) -> Round:
    db.session.add(round)
    db.session.commit()
    current_app.logger.info(f"Round added with round_id: '{round.round_id}.")
    return round


def update_round(round: Round) -> Round:
    db.session.commit()
    current_app.logger.info(f"Round updated with round_id: '{round.round_id}.")
    return round


def get_round_by_id(id: str) -> Round:
    round = db.session.get(Round, id)
    if not round:
        raise ValueError(f"Round with id {id} not found")
    return round


def get_all_rounds() -> list:
    stmt = select(Round).order_by(Round.short_name)
    return db.session.scalars(stmt).all()
