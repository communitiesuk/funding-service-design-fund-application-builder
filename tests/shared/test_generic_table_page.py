import json

import pytest

from app.shared.table_pagination import GovUKTableAndPagination

MORE_THAN_DEFAULT_START_FIRST_PAGE = """
{"items": [{"number": 1, "href": "?page=1", "current": true},
{"number": 2, "href": "?page=2"}, {"number": 3, "href": "?page=3"}], "next": {"href": "?page=2"}}"""
MORE_THAN_DEFAULT_START_SECOND_PAGE = """
{"items": [{"number": 1, "href": "?page=1"},
{"number": 2, "href": "?page=2", "current": true}, {"number": 3, "href": "?page=3"}],
"previous": {"href": "?page=1"}, "next": {"href": "?page=3"}}"""
MORE_THAN_DEFAULT_START_LAST_PAGE = """
{"items": [{"number": 1, "href": "?page=1"},
{"number": 2, "href": "?page=2"},
{"number": 3, "href": "?page=3", "current": true}], "previous": {"href": "?page=2"}}"""


def generate_data(rows) -> list[dict]:
    data = []
    for i in range(1, rows + 1):
        row = [
            {
                "html": "<a class='govuk-link--no-visited-state' "
                f"href='/index_bp/preview_form?form_id={i}'>Form Template {i}</a>"
            },
            {"text": f"Form Name {i}"},
            {"text": f"Form Runner Publish Name {i}"},
            {
                "html": "<a class='govuk-link--no-visited-state' href='"
                f"href='/index_bp/edit?form_id={i}'>Edit</a> &nbsp;"
                "<a class='govuk-link--no-visited-state' href='"
                f"href='/index_bp/delete?form_id={i}'>Delete</a>"
            },
        ]
        data.append(row)
    return data


@pytest.mark.parametrize(
    "pagination_scenario",
    [
        {
            "table_row_count": 0,
            "expected_pagination": None,  # row count is 0 so no pagination
            "current_page": 1,
        },
        {
            "table_row_count": 10,
            "expected_pagination": None,  # row count is 10 default pagination size is 20 so no pagination
            "current_page": 1,
        },
        {
            "table_row_count": 45,
            "expected_pagination": MORE_THAN_DEFAULT_START_FIRST_PAGE,
            # row count is 45 default pagination size is 20 so 3 pages pagination
            "current_page": 1,
        },
        {
            "table_row_count": 45,
            "expected_pagination": MORE_THAN_DEFAULT_START_SECOND_PAGE,
            # row count is 45 default pagination size is 20 so 3 pages pagination, next and previous
            "current_page": 2,
        },
        {
            "table_row_count": 45,
            "expected_pagination": MORE_THAN_DEFAULT_START_LAST_PAGE,
            # row count is 45 default pagination size is 20 so 3 pages pagination, previous only
            "current_page": 3,
        },
    ],
)
def test_pagination_with_less_than_pagination_default(pagination_scenario):
    gpt = GovUKTableAndPagination(
        table_header=[
            {"text": "Template Name"},
            {"text": "Tasklist Name"},
            {"text": "URL Path"},
            {"text": "Action"},
        ],
        table_rows=generate_data(pagination_scenario["table_row_count"]),
        current_page=pagination_scenario["current_page"],
    ).__dict__

    if pagination_scenario["expected_pagination"] is None:  # no pagination scenarios
        assert "pagination" not in gpt["table_pagination_page"], "Pagination not available"
        assert len(gpt["table_pagination_page"]["table"]["table_rows"]) == pagination_scenario["table_row_count"], (
            "Invalid table row count"
        )
    else:
        assert "pagination" in gpt["table_pagination_page"], "Pagination not available"
        assert gpt["table_pagination_page"]["pagination"] == json.loads(pagination_scenario["expected_pagination"]), (
            "Pagination invalid"
        )
        # check table data row data after pagination
        match pagination_scenario["current_page"]:
            case 1:
                assert len(gpt["table_pagination_page"]["table"]["table_rows"]) == 20, "Invalid table row count"
                assert "form_id=1" in str(gpt["table_pagination_page"]["table"]["table_rows"][0][0]), (
                    "Not starting from correct first data"
                )
                assert "form_id=20" in str(gpt["table_pagination_page"]["table"]["table_rows"][19][0]), (
                    "Not ending from correct last data"
                )
            case 2:
                assert len(gpt["table_pagination_page"]["table"]["table_rows"]) == 20, "Invalid table row count"
                assert "form_id=21" in str(gpt["table_pagination_page"]["table"]["table_rows"][0][0]), (
                    "Not starting from correct first data"
                )
                assert "form_id=40" in str(gpt["table_pagination_page"]["table"]["table_rows"][19][0]), (
                    "Not ending from correct last data"
                )
            case 3:
                assert len(gpt["table_pagination_page"]["table"]["table_rows"]) == 5, "Invalid table row count"
                assert "form_id=41" in str(gpt["table_pagination_page"]["table"]["table_rows"][0][0]), (
                    "Not starting from correct first data"
                )
                assert "form_id=45" in str(gpt["table_pagination_page"]["table"]["table_rows"][4][0]), (
                    "Not ending from correct last data"
                )
