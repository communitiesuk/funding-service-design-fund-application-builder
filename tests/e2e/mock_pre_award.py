import json

from flask import Flask, jsonify

app = Flask(__name__)

MOCK_FORMS = [
    {
        "id": "test-1",
        "url_path": "dataset-information",
        "display_name": "Dataset Information",
        "is_published": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "published_at": "2024-01-01T00:00:00Z",
    }
]


@app.route("/")
def get_forms():
    return jsonify(MOCK_FORMS)


@app.route("/<path:url_path>/published")
def get_published_form(url_path):
    with open("tests/e2e/fixtures/example-template.json") as f:
        template = json.load(f)

    return jsonify({**MOCK_FORMS[0], "published_json": template, "hash": "mock-hash"})


if __name__ == "__main__":
    app.run(port=8081)
