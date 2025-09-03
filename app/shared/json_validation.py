from jsonschema import validate

FORM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",  # NOSONAR
    "type": "object",
    "properties": {
        "startPage": {"type": "string"},
        "sections": {"type": "array"},
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "title": {"type": "string"},
                    "options": {"type": "object"},
                    "section": {"type": "string"},
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "options": {
                                    "type": "object",
                                    "properties": {"hideTitle": {"type": "boolean"}, "classes": {"type": "string"}},
                                },
                                "type": {"type": "string"},
                                "title": {"type": ["string", "null"]},
                                "content": {"type": ["string", "null"]},
                                "hint": {"type": "string"},
                                "schema": {
                                    "type": "object",
                                },
                                "name": {"type": "string"},
                                "metadata": {
                                    "type": "object",
                                },
                                "children": {"type": "array"},
                            },
                        },
                    },
                },
                "required": ["path", "title", "components"],
            },
        },
        "lists": {"type": "array"},
        "conditions": {"type": "array"},
        "outputs": {
            "type": "array",
        },
        "skipSummary": {"type": "boolean"},
        # Add other top-level keys as needed
    },
    "required": [
        "startPage",
        "pages",
        "lists",
        "conditions",
        "outputs",
        "skipSummary",
        "sections",
    ],
}


def validate_form_json(form_json):
    validate(instance=form_json, schema=FORM_SCHEMA)
