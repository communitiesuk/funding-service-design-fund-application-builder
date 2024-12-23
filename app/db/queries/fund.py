from flask import current_app
from sqlalchemy import select

from app.db import db
from app.db.models.fund import Fund, Organisation


def add_organisation(organisation: Organisation) -> Organisation:
    db.session.add(organisation)
    db.session.commit()
    return organisation


def add_fund(fund: Fund) -> Fund:
    db.session.add(fund)
    db.session.commit()
    current_app.logger.info(f"Fund added with fund_id: '{fund.fund_id}.")
    return fund


def update_fund(fund: Fund) -> Fund:
    db.session.commit()
    current_app.logger.info(f"Fund updated with fund_id: '{fund.fund_id}.")
    return fund


def get_all_funds() -> list:
    stmt = select(Fund).order_by(Fund.short_name)
    return db.session.scalars(stmt).all()


def get_fund_by_id(id: str) -> Fund:
    fund = db.session.get(Fund, id)
    if not fund:
        raise ValueError(f"Fund with id {id} not found")
    return fund


def get_fund_by_short_name(short_name: str) -> Fund:
    return db.session.query(Fund).filter_by(short_name=short_name).first()
