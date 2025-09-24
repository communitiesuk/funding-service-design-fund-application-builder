from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from app.db.queries.clone import clone_single_round, clone_single_section


@pytest.fixture
def mock_form():
    form = Mock()
    form.form_id = uuid4()
    form.section_id = uuid4()
    form.section_index = 1
    form.runner_publish_name = "test-form"
    form.as_dict.return_value = {
        "form_id": form.form_id,
        "section_id": form.section_id,
        "section_index": form.section_index,
        "runner_publish_name": form.runner_publish_name,
    }
    return form


@pytest.fixture
def mock_section():
    section = Mock()
    section.section_id = uuid4()
    section.round_id = uuid4()
    section.name_in_apply_json = {"en": "Test Section"}
    section.template_name = "test-section"
    section.is_template = True
    section.index = 1
    section.forms = [Mock()]  # Mock form list
    section.as_dict.return_value = {
        "name_in_apply_json": section.name_in_apply_json,
        "template_name": section.template_name,
        "index": section.index,
    }
    return section


@pytest.fixture
def mock_round():
    round_obj = Mock()
    round_obj.round_id = uuid4()
    round_obj.fund_id = uuid4()
    round_obj.title_json = {"en": "Test Round", "cy": "Test Round Welsh"}
    round_obj.short_name = "test-round"
    round_obj.is_template = True
    round_obj.sections = [Mock()]  # Mock section list
    round_obj.as_dict.return_value = {
        "title_json": round_obj.title_json,
        "short_name": round_obj.short_name,
        "is_template": round_obj.is_template,
    }
    return round_obj


def test_clone_single_section(mock_section):
    """Test that clone_single_section creates a new section and clones its forms."""
    # Arrange
    new_round_id = str(uuid4())

    with (
        patch("app.db.queries.clone.db") as mock_db,
        patch("app.db.queries.clone.insert_form") as mock_insert_form,
    ):
        # Mock database query
        mock_db.session.query.return_value.where.return_value.one_or_none.return_value = mock_section

        # Act
        cloned_section = clone_single_section(mock_section.section_id, new_round_id)

        # Assert
        assert cloned_section.section_id != mock_section.section_id
        assert cloned_section.round_id == new_round_id
        assert cloned_section.is_template is False
        assert cloned_section.source_template_id == mock_section.section_id
        assert cloned_section.template_name is None

        # Verify insert_form was called for each form
        assert mock_insert_form.call_count == len(mock_section.forms)
        mock_insert_form.assert_called_with(
            section_id=mock_section.section_id,
            url_path=mock_section.forms[0].url_path,
            section_index=mock_section.forms[0].section_index,
        )

        # Verify database operations
        mock_db.session.add.assert_called_once_with(cloned_section)
        mock_db.session.commit.assert_called_once()


def test_clone_single_round(mock_round):
    """Test that clone_single_round creates a new round and clones its sections."""
    # Arrange
    new_fund_id = str(uuid4())
    new_short_name = "cloned-round"

    # Calculate expected titles
    expected_en_title = "Copy of " + mock_round.title_json["en"]
    expected_cy_title = "Copi o " + mock_round.title_json["cy"]

    with (
        patch("app.db.queries.clone.db") as mock_db,
        patch("app.db.queries.clone.clone_single_section") as mock_clone_section,
    ):
        # Mock database query
        mock_db.session.query.return_value.where.return_value.one_or_none.return_value = mock_round

        # Act
        cloned_round = clone_single_round(mock_round.round_id, new_fund_id, new_short_name)

        # Assert
        assert cloned_round.round_id != mock_round.round_id
        assert cloned_round.fund_id == new_fund_id
        assert cloned_round.short_name == new_short_name
        assert cloned_round.is_template is False
        assert cloned_round.source_template_id == mock_round.round_id
        assert cloned_round.template_name is None
        assert cloned_round.sections == []
        assert cloned_round.section_base_path is None

        # Verify title was updated with "Copy of"
        assert cloned_round.title_json["en"] == expected_en_title
        assert cloned_round.title_json["cy"] == expected_cy_title

        # Verify sections were cloned
        assert mock_clone_section.call_count == len(mock_round.sections)

        # Verify database operations
        mock_db.session.add.assert_called_once_with(cloned_round)
        mock_db.session.commit.assert_called_once()
