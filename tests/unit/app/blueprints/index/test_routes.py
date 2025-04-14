from html import unescape
from unittest.mock import patch

import pytest

from config import Config


def test_index_redirects_to_login_for_unauthenticated_user(flask_test_client):
    """
    Tests that unauthenticated users are redirected to the login page when trying to access the index route.
    """
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_index_redirects_to_dashboard_for_authenticated_user(flask_test_client):
    """
    Tests that authenticated users are redirected to the dashboard when trying to access the index route.
    """
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/dashboard"


def test_login_renders_for_unauthenticated_user(flask_test_client):
    """
    Tests that the login page renders correctly for unauthenticated users.
    """
    response = flask_test_client.get("/login")
    assert response.status_code == 200
    assert b"Sign in to use FAB" in response.data

    html = response.data.decode("utf-8")
    assert "Sign out" not in html
    assert f"{Config.AUTHENTICATOR_HOST}/sessions/sign-out?return_app=fund-application-builder" not in unescape(html)


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_dashboard_renders_for_allowed_domain_user(flask_test_client):
    """
    Tests that authenticated users with allowed domains can access the dashboard.
    """
    response = flask_test_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Creating a new grant application" in response.data

    # Logged in user can see Sign out link
    html = response.data.decode("utf-8")
    assert "Sign out" in html
    assert f"{Config.AUTHENTICATOR_HOST}/sessions/sign-out?return_app=fund-application-builder" in unescape(html)


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_disallowed_domain_user")
def test_dashboard_forbidden_for_disallowed_domain_user(flask_test_client):
    """
    Tests that authenticated users with disallowed domains cannot access the dashboard.
    """
    response = flask_test_client.get("/dashboard")
    assert response.status_code == 403
    assert b"You do not have permission to access this page" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_internal_server_error(flask_test_client):
    """
    Tests that a 500 internal server error returns the custom 500 page.
    """
    # Temporarily disable exception propagation so the custom 500 handler is used
    old_prop_setting = flask_test_client.application.config["PROPAGATE_EXCEPTIONS"]
    flask_test_client.application.config["PROPAGATE_EXCEPTIONS"] = False

    try:
        with patch("app.blueprints.index.routes.get_form_by_id") as mock_get_form_by_id:
            mock_get_form_by_id.side_effect = Exception("Trigger 500 error")
            response = flask_test_client.get("/preview/9999")

        assert response.status_code == 500
        assert b"Sorry, there is a problem with the service" in response.data

    finally:
        # Restore the original setting
        flask_test_client.application.config["PROPAGATE_EXCEPTIONS"] = old_prop_setting


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_disallowed_domain_user")
def test_dashboard_respects_allowed_domains_config(flask_test_client):
    """
    Tests that the ALLOWED_DOMAINS config properly controls access.
    """
    # Save original config
    original_config = flask_test_client.application.config.get("ALLOWED_DOMAINS", "")

    try:
        # Set example.com as an allowed domain
        flask_test_client.application.config["ALLOWED_DOMAINS"] = "example.com"

        # With example.com now allowed, the "disallowed" user should be able to access
        response = flask_test_client.get("/dashboard")
        assert response.status_code == 200
        assert b"Creating a new grant application" in response.data

    finally:
        # Restore original config
        flask_test_client.application.config["ALLOWED_DOMAINS"] = original_config
