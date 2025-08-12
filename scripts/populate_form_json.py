"""
Script to populate the form_json column for existing forms.

This script generates form JSON for all forms that currently have NULL values
in the form_json column, using the existing form JSON generation logic.
"""

import sys

from flask import current_app
from sqlalchemy import text

from app.create_app import create_app
from app.db import db
from app.db.models import Form
from app.export_config.generate_form import build_form_json


def populate_form_json():
    """
    Populate the form_json column for all forms with NULL values.
    """
    print("Starting form JSON population script...")

    # Get all forms where form_json is NULL
    forms_to_update = db.session.query(Form).filter(Form.form_json.is_(None)).all()

    if not forms_to_update:
        print("No forms found with NULL form_json. All forms are already populated.")
        return

    print(f"Found {len(forms_to_update)} forms with NULL form_json")

    updated_count = 0
    error_count = 0

    for form in forms_to_update:
        try:
            form_name = form.name_in_apply_json.get("en", "Unnamed")
            print(f"Processing form: {form.form_id} - {form_name}")

            # Get fund title if the form is linked to a section with a round
            fund_title = None
            if form.section_id:
                # Get the round through the section to get the fund
                result = db.session.execute(
                    text("""
                        SELECT f.title_json
                        FROM fund f
                        JOIN round r ON f.fund_id = r.fund_id
                        JOIN section s ON r.round_id = s.round_id
                        WHERE s.section_id = :section_id
                    """),
                    {"section_id": form.section_id},
                ).fetchone()

                if result:
                    fund_title = result[0].get("en") if result[0] else None

            # Generate the form JSON using existing logic
            form_json = build_form_json(form=form, fund_title=fund_title)

            # Update the form with the generated JSON
            form.form_json = form_json

            updated_count += 1
            print(f"  ✓ Generated JSON for form {form.form_id}")

        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing form {form.form_id}: {str(e)}")
            current_app.logger.error(
                "Failed to generate JSON for form.", extra=dict(form_id=str(form.form_id), error=str(e))
            )

    try:
        # Commit all changes
        db.session.commit()
        print(f"\n✓ Successfully updated {updated_count} forms")
        if error_count > 0:
            print(f"✗ {error_count} forms failed to update")
        print("Form JSON population completed.")

    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Failed to commit changes: {str(e)}")
        current_app.logger.error("Failed to commit form JSON updates.", extra=dict(error=str(e)))
        sys.exit(1)


def main():
    """Main entry point for the script."""
    app = create_app()

    with app.app_context():
        try:
            populate_form_json()
        except Exception as e:
            print(f"Script failed with error: {str(e)}")
            current_app.logger.error("Form JSON population script failed.", extra=dict(error=str(e)))
            sys.exit(1)


if __name__ == "__main__":
    main()
