"""
This script deletes specified funds and rounds from the database. It first deletes rounds to
avoid foreign key constraint issues before deleting the corresponding funds. The funds and rounds
to delete are provided by predefined lists or can be specified via command-line arguments.


Process:
1. Deletes funds by English name from the `Fund` model.
2. Deletes rounds by fund name and round short name from the `Round` model.

Error Handling:
- Logs all actions and errors for traceability.
- Rolls back the session in case of an error during deletion.
"""

# flake8: noqa: E402
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # noqa: E402
sys.path.insert(0, project_root)  # noqa: E402

import argparse

from app.create_app import create_app
from app.db import db
from app.db.models.fund import Fund
from app.db.models.round import Round
from app.db.queries.fund import delete_selected_fund
from app.db.queries.round import delete_selected_round

# Funds to delete by English name
FUNDS_TO_DELETE = [
    "Crash Test Dummy Fund",
    "f",
    "Frog Road Safety Fund",
    "Jena Allen",
    "Madaline Hunter",
    "Napton Flower Festival",
    "Pauline's Fund",
    "Ruman's Fund 2024/2025",
    "Sarah Fund 1",
    "Water bottle fund",
]

# Rounds to delete by English name and fund English name and short name
ROUNDS_TO_DELETE = [
    {
        "fund_name": "Community Ownership Fund 2025",
        "round_short_name": "R-C816",
    },
    {
        "fund_name": "Community Ownership Fund 2025",
        "round_short_name": "R-C679",
    },
    {"fund_name": "Community Ownership Fund 2025", "round_name": "dcddewewwdwdw", "round_short_name": "123456"},
    {
        "fund_name": "Community Ownership Fund 2025",
        "round_short_name": "rfjs",
    },
    {"fund_name": "Napton Flower Festival", "round_short_name": "NFF"},
]


def delete_funds(fund_names=None):
    """Delete funds by English name from name_json"""
    funds_to_delete = fund_names or FUNDS_TO_DELETE
    print("\n=== Starting fund deletions ===")
    for fund_name in funds_to_delete:
        try:
            # Query using JSON field
            fund = Fund.query.filter(Fund.name_json["en"].astext == fund_name).first()

            if fund:
                print(f"Deleting fund: {fund_name} (ID: {fund.fund_id})")
                delete_selected_fund(fund.fund_id)
                print(f"✓ Successfully deleted fund: {fund_name}")
            else:
                print(f"❌ Fund not found: {fund_name}")
        except Exception as e:
            print(f"❌ Error deleting fund {fund_name}: {str(e)}")
            db.session.rollback()


def delete_rounds(rounds=None):
    """Delete rounds by English title and fund name"""
    rounds_to_delete = rounds or ROUNDS_TO_DELETE
    print("\n=== Starting round deletions ===")
    for round_info in rounds_to_delete:
        try:
            # First find the fund using the English name
            funds = Fund.query.filter(Fund.name_json["en"].astext == round_info["fund_name"]).all()

            if not funds:
                print(f"❌ Fund not found: {round_info['fund_name']}")
                continue
            for fund in funds:
                # Then find the round using the English title and fund_id
                round_obj = Round.query.filter(
                    Round.fund_id == fund.fund_id,
                    Round.short_name == round_info["round_short_name"],
                ).first()

                if round_obj:
                    print(f"Deleting round: {round_info['round_short_name']} from fund: {round_info['fund_name']}")
                    delete_selected_round(round_obj.round_id)
                    print(f"✓ Successfully deleted round: {round_info['round_short_name']}")
                else:
                    print(f"❌ Round not found: {round_info['round_short_name']} in fund: {round_info['fund_name']}")
        except Exception as e:
            print(f"❌ Error deleting round {round_info['round_short_name']}: {str(e)}")
            db.session.rollback()


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Delete specific funds and rounds from the database.")
    parser.add_argument(
        "--fund-name",
        type=str,
        help="The English name of the fund to delete. If not provided, defaults to predefined list.",
    )
    parser.add_argument(
        "--round-short-name",
        type=str,
        help="The short name of the round to delete. If not provided, deletes rounds from predefined list.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    app = create_app()  # Create the Flask app
    args = parse_arguments()  # Parse arguments

    with app.app_context():  # Create application context
        try:
            # Delete rounds first to avoid foreign key constraints
            if args.fund_name and args.round_short_name:
                print(f"\n✓ Deleting specific fund: {args.fund_name} and round: {args.round_short_name}")
                delete_rounds([{"fund_name": args.fund_name, "round_short_name": args.round_short_name}])
                delete_funds([args.fund_name])
            else:
                delete_rounds()
                # # Then delete funds
                delete_funds()
            print("\n✓ Deletion process completed")
        except Exception as e:
            print(f"\n❌ Fatal error during deletion process: {str(e)}")
            db.session.rollback()
