from app import app
from app.db import db
from app.db.models import Component, Condition, Page, PageCondition


# sonarignore
def run_migration():
    # Start Flask app context
    with app.app_context():
        try:
            # Query the Component table
            form_ids = []
            components_with_conditions = db.session.query(Component).where(Component.conditions != None).all()  # noqa: E711
            print(f"Number of components with condition: {len(components_with_conditions)}")

            for component in components_with_conditions:
                page = db.session.query(Page).where(Page.page_id == component.page_id).one_or_none()
                for condition in component.conditions:
                    condition = Condition(
                        name=condition["name"],
                        display_name=condition["display_name"],
                        value=condition["value"],
                        form_id=page.form_id,
                        is_template=page.is_template,
                        page_conditions=[
                            PageCondition(
                                page_id=page.page_id,
                                destination_page_path=condition["destination_page_path"],
                                is_template=page.is_template,
                            )
                        ],
                    )
                    db.session.add(condition)
                    form_ids.append(page.form_id)

            db.session.flush()

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")
            raise  # Re-raise if you want the script to crash on error


def _is_equivalent_empty(val1, val2):
    empty_values = ("", {}, [], None)
    return (val1 == val2) or (val1 in empty_values and val2 in empty_values)


if __name__ == "__main__":
    run_migration()
