import os

from invoke import task
from sqlalchemy import update

from app.db.models.fund import Fund
from app.db.models.round import Round

os.environ.update({"FLASK_ENV": "development"})

from app import app  # noqa:E402
from tasks.fake_funds.ctdf import LOADER_CONFIG as CTDF  # noqa:E402

"""
    Tasks to insert/update fake funds as they are added to the fake_funds folder
"""


@task
def upsert_ctdf(c):

    with app.app_context():
        db = app.extensions["sqlalchemy"]
        fund = {**CTDF["fund_config"]}
        fund.pop("owner_organisation_name")
        fund.pop("owner_organisation_shortname")
        fund.pop("owner_organisation_logo_uri")
        fund_to_upsert = Fund(fund_id=fund.pop("id"), is_template=False, **fund)
        fund_from_db = db.session.get(Fund, fund_to_upsert.fund_id)
        if not fund_from_db:
            db.session.add(fund_to_upsert)
        else:
            db.session.execute(
                update(Fund).where(Fund.fund_id == fund_to_upsert.fund_id).values(**fund_to_upsert.as_dict())
            )
        db.session.commit()
        round = {**CTDF["round_config"]}
        round_to_upsert = Round(
            round_id=round.pop("id"),
            prospectus_link=round.pop("prospectus"),
            privacy_notice_link=round.pop("privacy_notice"),
            is_template=False,
            **round,
        )
        round_from_db = db.session.get(Round, round_to_upsert.round_id)
        if not round_from_db:
            db.session.add(round_to_upsert)
        else:
            db.session.execute(
                update(Round).where(Round.round_id == round_to_upsert.round_id).values(**round_to_upsert.as_dict())
            )
        db.session.commit()
