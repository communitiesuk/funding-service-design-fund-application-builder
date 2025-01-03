import pytest
from flask import url_for


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_select_fund(flask_test_client, seed_dynamic_data):
    """
    Test the /rounds/sections/select-fund route to ensure:
      1) A user cannot proceed without selecting a fund,
      2) A valid fund selection redirects to the select_application page.
    """
    # Attempt to submit without a fund selected
    with pytest.raises(ValueError, match="Fund ID is required to manage an application"):
        flask_test_client.post(
            "/rounds/sections/select-fund",
            data={"fund_id": ""},
            follow_redirects=True,
        )

    # Submit with a valid fund
    test_fund = seed_dynamic_data["funds"][0]
    response = flask_test_client.post(
        "/rounds/sections/select-fund", data={"fund_id": str(test_fund.fund_id)}, follow_redirects=False
    )
    assert response.status_code == 302

    # Confirm redirect to the application_bp.select_application route
    expected_location = url_for("application_bp.select_application", fund_id=test_fund.fund_id)
    assert response.location == expected_location


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_select_application(flask_test_client, seed_dynamic_data):
    """
    Test the /rounds/sections/select-application route to ensure:
      1) A user cannot proceed without selecting an application,
      2) A valid application selection redirects to the build_application page.
    """
    # Attempt to see the page without a fund ID
    with pytest.raises(ValueError, match="Fund ID is required to manage an application"):
        flask_test_client.get("/rounds/sections/select-application", follow_redirects=True)

    # Attempt to see the page with an invalid fund ID
    invalid_fund_id = "123e4567-e89b-12d3-a456-426614174000"
    with pytest.raises(ValueError, match=f"Fund with id {invalid_fund_id} not found"):
        flask_test_client.get(f"/rounds/sections/select-application?fund_id={invalid_fund_id}", follow_redirects=True)

    # Attempt to submit without a round selected
    with pytest.raises(ValueError, match="Round ID is required to manage an application"):
        flask_test_client.post(
            "/rounds/sections/select-application",
            data={"round_id": ""},
            follow_redirects=True,
        )

    # Submit with a valid round
    test_round = seed_dynamic_data["rounds"][0]
    response = flask_test_client.post(
        f"/rounds/sections/select-application?fund_id={test_round.fund_id}",
        data={"round_id": str(test_round.round_id)},
        follow_redirects=False,
    )
    assert response.status_code == 302

    # Confirm redirect to application_bp.build_application
    expected_location = url_for("application_bp.build_application", round_id=test_round.round_id)
    assert response.location == expected_location
