import pytest


def test_index_redirects_to_login_for_unauthenticated_user(flask_test_client):
    """
    Tests that unauthenticated users are redirected to the login page when trying to access the index route.
    """
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_dashboard_renders_for_internal_user(flask_test_client):
    """
    Tests that authenticated internal users can access the dashboard.
    """
    response = flask_test_client.get("/dashboard")
    assert response.status_code == 200
    assert b"What do you want to do?" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_external_user")
def test_dashboard_forbidden_for_external_user(flask_test_client):
    """
    Tests that authenticated external users are forbidden from accessing the dashboard.
    """
    response = flask_test_client.get("/dashboard")
    assert response.status_code == 403
    assert b"You do not have permission to access this page" in response.data
