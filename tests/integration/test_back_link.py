import pytest
from flask import session, url_for


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_session_track_visited_pages_fund(flask_test_client, seed_dynamic_data):
    with flask_test_client.session_transaction():
        test_fund = seed_dynamic_data["funds"][0]
        # Simulate visiting a page
        flask_test_client.get(url_for("fund_bp.view_all_funds"))
        flask_test_client.get(url_for("fund_bp.view_fund_details", fund_id=test_fund.fund_id))
        flask_test_client.get(url_for("fund_bp.edit_fund", fund_id=test_fund.fund_id))
        assert len(session["visited_pages"]) == 3
        assert session["visited_pages"][0]["endpoint"] == "fund_bp.view_all_funds"
        assert session["visited_pages"][1]["endpoint"] == "fund_bp.view_fund_details"
        assert session["visited_pages"][2]["endpoint"] == "fund_bp.edit_fund"

        response = flask_test_client.get(url_for("index_bp.go_back"))
        assert response.status_code == 302
        assert response.headers["Location"] == url_for("fund_bp.view_fund_details", fund_id=test_fund.fund_id)

        response = flask_test_client.get(url_for("index_bp.go_back"))
        assert response.status_code == 302
        assert response.headers["Location"] == url_for("fund_bp.view_all_funds")


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_session_track_visited_pages_template(flask_test_client, seed_dynamic_data):
    with flask_test_client.session_transaction():
        test_form = seed_dynamic_data["forms"][0]
        # Simulate visiting a page
        flask_test_client.get(url_for("template_bp.view_templates"))
        flask_test_client.get(url_for("template_bp.template_details", form_id=test_form.form_id))
        flask_test_client.get(url_for("template_bp.edit_template", form_id=test_form.form_id))
        assert len(session["visited_pages"]) == 3
        assert session["visited_pages"][0]["endpoint"] == "template_bp.view_templates"
        assert session["visited_pages"][1]["endpoint"] == "template_bp.template_details"
        assert session["visited_pages"][2]["endpoint"] == "template_bp.edit_template"

        response = flask_test_client.get(url_for("index_bp.go_back"))
        assert response.status_code == 302
        assert response.headers["Location"] == url_for("template_bp.template_details", form_id=test_form.form_id)

        response = flask_test_client.get(url_for("index_bp.go_back"))
        assert response.status_code == 302
        assert response.headers["Location"] == url_for("template_bp.view_templates")


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
@pytest.mark.parametrize(
    "endpoint, expected_endpoint",
    [
        ("fund_bp.view_all_funds", "fund_bp.view_all_funds"),
        ("template_bp.view_templates", "template_bp.view_templates"),
        ("round_bp.view_all_rounds", "round_bp.view_all_rounds"),
    ],
)
def test_session_track_visited_pages_reset_session(flask_test_client, seed_dynamic_data, endpoint, expected_endpoint):
    with flask_test_client.session_transaction():
        # Simulate visiting a page and reset once navigating to the given endpoint
        _visit_template(flask_test_client, seed_dynamic_data)
        assert len(session["visited_pages"]) == 3
        flask_test_client.get(url_for(endpoint))
        assert len(session["visited_pages"]) == 1
        assert session["visited_pages"][0]["endpoint"] == expected_endpoint


def _visit_template(flask_test_client, seed_dynamic_data):
    test_form = seed_dynamic_data["forms"][0]
    # Simulate visiting a page
    flask_test_client.get(url_for("template_bp.view_templates"))
    flask_test_client.get(url_for("template_bp.template_details", form_id=test_form.form_id))
    flask_test_client.get(url_for("template_bp.edit_template", form_id=test_form.form_id))
    return test_form
