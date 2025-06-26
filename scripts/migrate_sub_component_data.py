from app import app
from app.db import db
from app.db.models import Component, ComponentType, Lizt
from app.export_config.generate_form import build_component
from app.shared.helpers import find_enum


# sonarignore
def run_migration():
    # Start Flask app context
    with app.app_context():
        try:
            # Query the Component table
            components_with_children = db.session.query(Component).where(Component.children != None).all()  # noqa: E711
            print(f"Number of components with children: {len(components_with_children)}")
            number_of_components_created = 0
            for parent_component in components_with_children:
                for children_component_idx, child_component in enumerate(parent_component.children):
                    component_type = child_component.get("type", None)

                    if component_type is None or find_enum(ComponentType, component_type) is None:
                        raise ValueError(f"Component type not found: {component_type}")

                    confirmed_component_type = find_enum(ComponentType, component_type)
                    list_name = child_component.get("list", None)

                    list_identify = None
                    if list_name is not None:
                        list_identify = db.session.query(Lizt).where(Lizt.name == list_name).first()

                    new_component = Component(
                        title=child_component.get("title", None),
                        content=child_component.get("content", None),
                        hint_text=child_component.get("hint", None),
                        options=child_component.get("options", None),
                        type=confirmed_component_type,
                        template_name=child_component.get("title"),
                        is_template=parent_component.is_template,
                        page_index=children_component_idx + 1,
                        runner_component_name=child_component.get("name", None),
                        list_id=list_identify.list_id if list_identify else None,
                        schema=child_component.get("schema", None),
                        parent_component=parent_component,
                    )
                    number_of_components_created = number_of_components_created + 1
                    db.session.add(new_component)

            for p_component in components_with_children:
                json_child_config = p_component.children
                new_json_child_config = []
                for child_component in p_component.children_components:
                    new_json_child_config.append(build_component(child_component))

                for children_component_idx, child_component in enumerate(json_child_config):  # noqa: B007
                    filter_new_component = [
                        comp for comp in new_json_child_config if comp["name"] == child_component["name"]
                    ]
                    assert len(filter_new_component) == 1, (
                        f"Multiple components with name {child_component['name']} found"
                    )
                    for key in child_component:
                        assert _is_equivalent_empty(child_component[key], filter_new_component[0][key]), (
                            f"Error: {key} {child_component[key]} != {filter_new_component[0][key]}"
                        )

            db.session.flush()
            components_with_children = db.session.query(Component).where(Component.parent_component_id != None).all()  # noqa: E711

            assert len(components_with_children) == number_of_components_created
            print(
                f"Number of components with children: {len(components_with_children)} created {number_of_components_created}"  # noqa: E501
            )
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
