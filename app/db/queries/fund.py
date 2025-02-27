from flask import current_app
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import String, cast, select
from sqlalchemy.orm import joinedload

from app.db import db
from app.db.models import Component, Form, Lizt, Page, Round
from app.db.models.fund import Fund, Organisation
from app.db.queries.util import delete_all_related_objects


def add_organisation(organisation: Organisation) -> Organisation:
    db.session.add(organisation)
    db.session.commit()
    return organisation


def add_fund(fund: Fund) -> Fund:
    db.session.add(fund)
    db.session.commit()
    current_app.logger.info("Fund added with fund_id: '{fund_id}'.", extra=dict(fund_id=fund.fund_id))
    return fund


def update_fund(fund: Fund) -> Fund:
    db.session.commit()
    current_app.logger.info("Fund updated with fund_id: '{fund_id}'.", extra=dict(fund_id=fund.fund_id))
    return fund


def get_all_funds() -> list[Fund]:
    stmt = select(Fund).order_by(cast(Fund.name_json["en"], String))
    return db.session.scalars(stmt).all()


def get_paginated_funds(page: int, items_per_page: int = 20) -> Pagination:
    stmt = select(Fund).order_by(cast(Fund.name_json["en"], String))
    return db.paginate(stmt, page=page, per_page=items_per_page)


def get_fund_by_id(id: str) -> Fund:
    fund = db.session.get(Fund, id)
    if not fund:
        raise ValueError(f"Fund with id {id} not found")
    return fund


def get_fund_by_short_name(short_name: str) -> Fund:
    return db.session.query(Fund).filter_by(short_name=short_name).first()


def _delete_sections_for_fund_round(fund: Fund):
    for round_detail in fund.rounds:
        for section in round_detail.sections:
            if section:
                lizt_ids = [
                    component.list_id for form in section.forms for page in form.pages for component in page.components
                ]
                page_ids = [page.page_id for form in section.forms for page in form.pages]
                form_ids = [form.form_id for form in section.forms]
                section_ids = [section.section_id]

                delete_all_related_objects(db=db, model=Component, column=Component.page_id, ids=page_ids)
                delete_all_related_objects(db=db, model=Lizt, column=Lizt.list_id, ids=lizt_ids)
                delete_all_related_objects(db=db, model=Page, column=Page.form_id, ids=form_ids)
                delete_all_related_objects(db=db, model=Form, column=Form.section_id, ids=section_ids)

                db.session.delete(section)
                db.session.commit()


def delete_selected_fund(fund_id):
    fund: Fund = db.session.get(Fund, fund_id, options=[joinedload(Fund.rounds).joinedload(Round.sections)])
    if not fund:
        raise ValueError(f"Fund with id {fund_id} not found")
    try:
        _delete_sections_for_fund_round(fund)
        delete_all_related_objects(
            db=db, model=Round, column=Round.round_id, ids=[round_detail.round_id for round_detail in fund.rounds]
        )
        delete_all_related_objects(db=db, model=Fund, column=Fund.fund_id, ids=[fund_id])
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Failed to delete fund {fund_id} : Error {e}")
