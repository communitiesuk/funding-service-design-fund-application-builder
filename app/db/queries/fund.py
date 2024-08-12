from sqlalchemy import select

from app.db import db
from app.db.models.fund import Fund
from app.db.models.fund import Organisation


def add_organisation(organisation: Organisation) -> Organisation:
    db.session.add(organisation)
    db.session.commit()
    return organisation


def add_fund(fund: Fund) -> Fund:
    db.session.add(fund)
    db.session.commit()
    return fund


def get_all_funds() -> list:
    stmt = select(Fund).order_by(Fund.short_name)
    return db.session.scalars(stmt).all()


def get_fund_by_id(id: str) -> Fund:
    fund = db.session.get(Fund, id)
    if not fund:
        raise ValueError(f"Fund with id {id} not found")
    return fund
