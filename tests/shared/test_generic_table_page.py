from app.shared.generic_table_page import GenericTablePage


def test_basic_initialization():
    """Test basic initialization and conversion to dictionary."""
    page = GenericTablePage(
        page_heading="Test Page",
        page_description="This is a test page.",
        detail_text="Test Detail",
        detail_description="This is a test detail description.",
        button_text="Test Button",
        button_url="https://example.com",
        table_header=[{"column": "Header1"}, {"column": "Header2"}],
        table_rows=[{"data": "Row1"}, {"data": "Row2"}],
    )

    result = page.__dict__

    assert result["page_heading"] == "Test Page"
    assert result["page_description"] == "This is a test page."
    assert result["detail"] == {
        "detail_text": "Test Detail",
        "detail_description": "This is a test detail description.",
    }
    assert result["button"] == {
        "button_text": "Test Button",
        "button_url": "https://example.com",
    }
    assert result["table"] == {
        "table_header": [{"column": "Header1"}, {"column": "Header2"}],
        "table_rows": [{"data": "Row1"}, {"data": "Row2"}],
    }


def test_without_mandatory_fields():
    """Test basic initialization and conversion to dictionary."""
    try:
        GenericTablePage(
            page_description="This is a test page.",
            detail_text="Test Detail",
            detail_description="This is a test detail description.",
            button_text="Test Button",
            button_url="https://example.com",
            table_header=[{"column": "Header1"}, {"column": "Header2"}],
            table_rows=[{"data": "Row1"}, {"data": "Row2"}],
        )
        assert AssertionError("Expected ValueError for invalid notification_banner_heading_type")
    except TypeError:
        pass
