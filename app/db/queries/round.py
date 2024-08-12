from app.db import db
from app.db.models.round import Round


def add_round(round: Round) -> Round:
    db.session.add(round)
    db.session.commit()
    return round


def get_round_by_id(id: str) -> Round:
    round = db.session.get(Round, id)
    if not round:
        raise ValueError(f"Round with id {id} not found")
    return round
