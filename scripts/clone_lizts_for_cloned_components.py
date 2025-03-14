"""
This script clones `Lizt` records associated with `Component` records that are not templates
and have a `list_id`. For each valid component, the script performs the following actions:

1. Identifies components that are not templates (`is_template=False`) and have a `list_id`.
2. For each such component, the script fetches the existing `Lizt` record that corresponds to the
`list_id` of the component.
3. It clones the `Lizt` record by creating a new `Lizt` with a new `list_id` while retaining all other
attributes (`name`, `title`, `type`, `items`).
4. The component is then updated to point to the newly cloned `Lizt`.
5. After all components are processed, the script commits the changes to the database.

Error Handling:
- If any error occurs during the cloning process, the transaction is rolled back to ensure data consistency.

Usage:
Run this script within a Flask app context to clone the Lizt objects for associated
components that are not templates.
This script is run only once if we don't have cloning of lizts

Requirements:
- Proper models (`Component` and `Lizt`) in the `application_config` module.
"""

# flake8: noqa: E402
import os
import sys

# Add the root directory of the project to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # noqa: E402
sys.path.insert(0, project_root)  # noqa: E402

import uuid

from app.create_app import create_app
from app.db import db
from app.db.models.application_config import Component, Lizt


def clone_lizt_for_components():
    # Fetch all cloned components that have a list_id
    components = Component.query.filter_by(is_template=False).filter(Component.list_id.isnot(None))
    print("\n=== Starting Cloning Lizts for cloned components ===")
    for component in components:
        # Fetch the existing Lizt
        old_lizt = Lizt.query.filter_by(list_id=component.list_id).first()
        if old_lizt:
            # Clone the Lizt
            new_lizt = Lizt(
                list_id=uuid.uuid4(),
                name=old_lizt.name,
                title=old_lizt.title,
                type=old_lizt.type,
                items=old_lizt.items,
                is_template=False,
            )
            db.session.add(new_lizt)
            db.session.flush()  # Ensure ID is generated

            # Update the component to point to the new Lizt
            component.list_id = new_lizt.list_id
            db.session.add(component)

    db.session.commit()
    print("✓ Successfully cloned Lizts")


if __name__ == "__main__":
    app = create_app()  # Create the Flask app
    with app.app_context():  # Create application context
        try:
            # clone lizt for cloned components where were pointing to template lizts
            clone_lizt_for_components()
            print("\n✓ Cloning process completed")
        except Exception as e:
            print(f"\n❌ Fatal error during cloning process: {str(e)}")
            db.session.rollback()
