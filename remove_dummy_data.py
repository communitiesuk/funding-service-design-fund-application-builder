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

# Rounds to delete by English name and fund English name
ROUNDS_TO_DELETE = [
    {"fund_name": "Madaline Hunter", "round_name": "Round 1"},
    {"fund_name": "Madaline Hunter", "round_name": "Est et tempora qui q"},
    {"fund_name": "Community Ownership Fund 2025", "round_name": "High Street Rental Auctions - Round 3"},
    {"fund_name": "Community Ownership Fund 2025", "round_name": "dcddewewwdwdw"},
    {"fund_name": "Community Ownership Fund 2025", "round_name": "ruman-fund-24-25-jul-sep"},
    {"fund_name": "Frog Road Safety Fund", "round_name": "Mr"},
    {"fund_name": "Crash Test Dummy Fund", "round_name": "Crash Round 1"},
    {"fund_name": "Napton Flower Festival", "round_name": "Round 5"},
    {"fund_name": "Water bottle fund", "round_name": "Round 1"},
]


def delete_funds():
    """Delete funds by English name from name_json"""
    print("\n=== Starting fund deletions ===")
    for fund_name in FUNDS_TO_DELETE:
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


def delete_rounds():
    """Delete rounds by English title and fund name"""
    print("\n=== Starting round deletions ===")
    for round_info in ROUNDS_TO_DELETE:
        try:
            # First find the fund using the English name
            fund = Fund.query.filter(Fund.name_json["en"].astext == round_info["fund_name"]).first()

            if not fund:
                print(f"❌ Fund not found: {round_info['fund_name']}")
                continue

            # Then find the round using the English title and fund_id
            round_obj = Round.query.filter(
                Round.fund_id == fund.fund_id, Round.title_json["en"].astext == round_info["round_name"]
            ).first()

            if round_obj:
                print(f"Deleting round: {round_info['round_name']} from fund: {round_info['fund_name']}")
                delete_selected_round(round_obj.round_id)
                print(f"✓ Successfully deleted round: {round_info['round_name']}")
            else:
                print(f"❌ Round not found: {round_info['round_name']} in fund: {round_info['fund_name']}")
        except Exception as e:
            print(f"❌ Error deleting round {round_info['round_name']}: {str(e)}")
            db.session.rollback()


if __name__ == "__main__":
    try:
        # Delete rounds first to avoid foreign key constraints
        delete_rounds()
        # Then delete funds
        delete_funds()
        print("\n✓ Deletion process completed")
    except Exception as e:
        print(f"\n❌ Fatal error during deletion process: {str(e)}")
        db.session.rollback()
