from sqlalchemy import select

from app.db import db
from app.db.models import Round


def get_round_by_title(title: str) -> Round:
    """
    Retrieves a Round object by its title

    Args:
        title: The title of the round to retrieve

    Returns:
        The Round object with the given title

    Raises:
        ValueError: If no Round with the given title is found
    """
    stmt = select(Round).where(Round.title_json["en"].astext == title)
    round = db.session.scalars(stmt).first()
    if not round:
        raise ValueError(f"Round with title '{title}' not found")
    return round


def get_csrf_token(response):
    """
    Extracts the CSRF token from the given response.

    Args:
        response: The response to extract the CSRF token from

    Returns:
        The CSRF token
    """
    return response.data.decode().split('name="csrf_token" type="hidden" value="')[1].split('"')[0]


def submit_form(flask_test_client, url, data, follow_redirects=True):
    """
    Submits a form given a flask test client, url, and the form data.

    Args:
        flask_test_client: The flask test client to use.
        url: The url of the form to submit.
        data: The data to submit on the form.
        follow_redirects: Whether to follow redirects after form submission.

    Returns:
        The response from submitting the form.
    """
    response = flask_test_client.get(url)
    csrf_token = get_csrf_token(response)
    data["csrf_token"] = csrf_token
    return flask_test_client.post(
        url, data=data, follow_redirects=follow_redirects, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
