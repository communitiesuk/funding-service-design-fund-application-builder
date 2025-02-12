import json
from unittest.mock import MagicMock
from flask_sqlalchemy.pagination import Pagination
import pytest
from app.shared.helpers import pagination_convertor

MORE_THAN_DEFAULT_START_FIRST_PAGE = """
{"next": {"href": "?page=2"}, "items": [{"number": 1, "href": "?page=1", "current": true}, 
{"number": 2, "href": "?page=2", "current": false}, {"ellipsis": true}, 
{"number": 20, "href": "?page=20", "current": false}]}
"""
MORE_THAN_DEFAULT_START_SECOND_PAGE = """
{"previous": {"href": "?page=1"}, "next": {"href": "?page=3"}, "items": [
{"number": 1, "href": "?page=1", "current": false}, 
{"number": 2, "href": "?page=2", "current": true}, 
{"number": 3, "href": "?page=3", "current": false}, {"ellipsis": true}, 
{"number": 20, "href": "?page=20", "current": false}]}
"""
MORE_THAN_DEFAULT_START_MIDDLE_PAGE = """
{"previous": {"href": "?page=9"}, "next": {"href": "?page=11"}, "items": [
{"number": 1, "href": "?page=1", "current": false}, {"ellipsis": true}, 
{"number": 9, "href": "?page=9", "current": false}, {"number": 10, "href": "?page=10", "current": true}, 
{"number": 11, "href": "?page=11", "current": false}, {"ellipsis": true}, 
{"number": 20, "href": "?page=20", "current": false}]}
"""
MORE_THAN_DEFAULT_START_LAST_PAGE = """
{"previous": {"href": "?page=19"}, "items": [{"number": 1, "href": "?page=1", "current": false}, {"ellipsis": true}, 
{"number": 19, "href": "?page=19", "current": false}, {"number": 20, "href": "?page=20", "current": true}]}
"""


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
pagination_higher_than_limit_middle = create_mock_pagination(
    page=10,
    pages=20,
    has_next=True,
    has_prev=True,
    next_num=11,
    prev_num=9,
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
            "expected_pagination": MORE_THAN_DEFAULT_START_FIRST_PAGE,
            "pagination": pagination_higher_than_limit_first
        },
        {  # when page count is more than one pagination available and check the following combination 1,2,3,...,20
            "expected_pagination": MORE_THAN_DEFAULT_START_SECOND_PAGE,
            "pagination": pagination_higher_than_limit_second
        },
        {
            # when page count is more than one pagination available and check the following combination 1,...,9,10,11,...,20 noqa: E501
            "expected_pagination": MORE_THAN_DEFAULT_START_MIDDLE_PAGE,
            "pagination": pagination_higher_than_limit_middle
        },
        {
            # when page count is more than one pagination available and check the following combination 1,...,19,20 noqa: E501
            "expected_pagination": MORE_THAN_DEFAULT_START_LAST_PAGE,
            "pagination": pagination_higher_than_limit_last
        },
    ],
)
def test_pagination_with_less_than_pagination_default(pagination_scenario):
    gpt = pagination_convertor(pagination=pagination_scenario["pagination"])
    if pagination_scenario["expected_pagination"] is None:  # no pagination scenarios
        assert gpt is None, "Pagination available"
    else:
        assert gpt is not None, "Pagination not available"
        pagination_json = json.loads(pagination_scenario.get("expected_pagination"))
        assert gpt == pagination_json, "Pagination is invalid"
