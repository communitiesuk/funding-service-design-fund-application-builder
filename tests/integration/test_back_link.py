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
@pytest.mark.parametrize(
    "reset_endpoint, expected_endpoint",
    [
        ("fund_bp.view_all_funds", "fund_bp.view_all_funds"),
        ("round_bp.view_all_rounds", "round_bp.view_all_rounds"),
        ("index_bp.dashboard", "index_bp.dashboard"),
    ],
)
def test_session_track_visited_pages_reset_session(
    flask_test_client, seed_dynamic_data, reset_endpoint, expected_endpoint
):
    with flask_test_client.session_transaction():
        # First, build up some navigation history
        test_fund = seed_dynamic_data["funds"][0]
        flask_test_client.get(url_for("fund_bp.view_fund_details", fund_id=test_fund.fund_id))
        flask_test_client.get(url_for("fund_bp.edit_fund", fund_id=test_fund.fund_id))

        # Verify we have some history
        with flask_test_client.session_transaction() as sess:
            assert len(sess["visited_pages"]) == 2

        # Now visit a reset endpoint
        flask_test_client.get(url_for(reset_endpoint))

        # Verify the session was reset to contain only the reset endpoint
        with flask_test_client.session_transaction() as sess:
            assert len(sess["visited_pages"]) == 1
            assert sess["visited_pages"][0]["endpoint"] == expected_endpoint
