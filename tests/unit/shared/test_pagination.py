import json
from unittest.mock import MagicMock
from flask_sqlalchemy.pagination import Pagination
from flask import render_template
from bs4 import BeautifulSoup
import pytest


def create_mock_pagination(
        page=1,
        has_next=False,
        has_prev=False,
        next_num=None,
        prev_num=None,
        pages=1,
):
    mock_pagination = MagicMock(spec=Pagination)
    mock_pagination.page = page
    mock_pagination.has_next = has_next
    mock_pagination.has_prev = has_prev
    mock_pagination.next_num = next_num
    mock_pagination.prev_num = prev_num
    mock_pagination.pages = pages
    return mock_pagination


# Pagination with total items less than the limit
pagination_lower_than_limit = create_mock_pagination(
    pages=1,
    has_next=False,
    has_prev=False,
)

# Pagination with total items exceeding the limit, on the first page
pagination_higher_than_limit_first = create_mock_pagination(
    page=1,
    pages=20,
    has_next=True,
    has_prev=False,
    next_num=2,
)

# Pagination with total items exceeding the limit, on the second page
pagination_higher_than_limit_second = create_mock_pagination(
    page=2,
    pages=20,
    has_next=True,
    has_prev=True,
    next_num=3,
    prev_num=1,
)

# Pagination with total items exceeding the limit, on the second page
pagination_higher_than_limit_third = create_mock_pagination(
    page=3,
    pages=20,
    has_next=True,
    has_prev=True,
    next_num=4,
    prev_num=2,
)

# Pagination with total items exceeding the limit, on the second page
pagination_higher_than_limit_middle = create_mock_pagination(
    page=10,
    pages=20,
    has_next=True,
    has_prev=True,
    next_num=11,
    prev_num=9,
)

# Pagination with total items exceeding the limit, on the one page before last page
pagination_higher_than_limit_one_before_last = create_mock_pagination(
    page=19,
    pages=20,
    has_next=True,
    has_prev=True,
    prev_num=18,
    next_num=20,
)

# Pagination with total items exceeding the limit, on the two pages before last page
pagination_higher_than_limit_two_before_last = create_mock_pagination(
    page=18,
    pages=20,
    has_next=True,
    has_prev=True,
    prev_num=17,
    next_num=18,
)

# Pagination with total items exceeding the limit, on the last page
pagination_higher_than_limit_last = create_mock_pagination(
    page=20,
    pages=20,
    has_next=False,
    has_prev=True,
    prev_num=19,
)


@pytest.mark.parametrize(
    "pagination_scenario",
    [
        {  # when page count is 1 no pagination
            "expected_pagination": None,
            "pagination": pagination_lower_than_limit
        },
        {  # when page count is more than one pagination available and check the following combination 1,2,...,20
            "expected_pagination": [1, 2, 20],
            "active_page": 1,
            "pagination": pagination_higher_than_limit_first
        },
        {  # when page count is more than one pagination available and check the following combination 1,2,3,...,20
            "expected_pagination": [1, 2, 3, 20],
            "active_page": 2,
            "pagination": pagination_higher_than_limit_second
        },
        {  # when page count is more than one pagination available and check the following combination 1,2,3,4,...,20
            "expected_pagination": [1, 2, 3, 4, 20],
            "active_page": 3,
            "pagination": pagination_higher_than_limit_third
        },
        {
            # when page count is more than one pagination available and check the following combination 1,...,9,10,11,...,20 noqa: E501
            "expected_pagination": [1, 9, 10, 11, 20],
            "active_page": 10,
            "pagination": pagination_higher_than_limit_middle
        },
        {
            # when page count is more than one pagination available and check the following combination 1,...,17,18,19,20 noqa: E501
            "expected_pagination": [1, 17, 18, 19, 20],
            "active_page": 18,
            "pagination": pagination_higher_than_limit_two_before_last
        },
        {
            # when page count is more than one pagination available and check the following combination 1,...,18,19,20 noqa: E501
            "expected_pagination": [1, 18, 19, 20],
            "active_page": 19,
            "pagination": pagination_higher_than_limit_one_before_last
        },
        {
            # when page count is more than one pagination available and check the following combination 1,...,19,20 noqa: E501
            "expected_pagination": [1, 19, 20],
            "active_page": 20,
            "pagination": pagination_higher_than_limit_last
        },
    ],
)
@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_pagination_with_less_than_pagination_default(app, pagination_scenario):
    with app.test_request_context():
        page = render_template("view_all_funds.html", table_rows=[], pagination=pagination_scenario["pagination"])
        actual_html = BeautifulSoup(page, "html.parser")

        if pagination_scenario["expected_pagination"] is None:  # no pagination scenarios
            pagination_available = actual_html.find("nav", attrs={"aria-label": "Pagination"})
            assert pagination_available is None, "Pagination available"
        else:
            pagination_element = actual_html.find("nav", attrs={"aria-label": "Pagination"})
            assert pagination_element is not None, "Pagination not available"

            page_links = [int(link.get_text(strip=True)) for link in
                          actual_html.find_all('a', class_='govuk-pagination__link') if not link.find('span')]
            # Check if the page numbers match the expected ones
            assert page_links == pagination_scenario["expected_pagination"]

            # Ensure that ellipses are present in the correct spots
            ellipses = actual_html.find_all('li', class_='govuk-pagination__item--ellipses')
            if '⋯' in page or '&ctdot;' in page:
                assert len(ellipses) >= 1  # We expect at least one ellipsis
            else:
                assert len(ellipses) == 0  # No ellipses should appear if there are no gaps

            # Check if the current page is set correctly
            active_page = actual_html.find('li', class_='govuk-pagination__item--current')
            active_page_number = int(active_page.find('a')['aria-label'].split()[-1])  # Extract page number
            assert active_page_number == pagination_scenario['active_page']
