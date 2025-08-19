import json
from unittest.mock import Mock, patch

import pytest

from app.db.models.application_config import ComponentType
from app.export_config.generate_assessment_config import _get_component_type, generate_assessment_config_for_round


class TestGetComponentType:
    def test_valid_component_type(self):
        component = {"type": "TextField"}
        result = _get_component_type(component)
        assert result == ComponentType.TEXT_FIELD

    def test_missing_component_type(self):
        component = {}
        with pytest.raises(ValueError, match="Component type not found: None"):
            _get_component_type(component)

    def test_invalid_component_type(self):
        component = {"type": "InvalidType"}
        with pytest.raises(ValueError, match="Component type not found: InvalidType"):
            _get_component_type(component)


class TestGenerateAssessmentConfig:
    @pytest.fixture
    def configs(self):
        fund_config = {"id": "fund-123", "short_name": "test_fund"}
        round_config = {"id": "round-456", "short_name": "round_1"}
        return fund_config, round_config

    @pytest.fixture
    def mock_form_data(self):
        mock_form = Mock()
        mock_form.runner_publish_name = "test-form"
        mock_form.name_in_apply_json = {"en": "Test Form"}
        mock_form.form_json = {
            "pages": [
                {
                    "path": "/contact",
                    "title": "Contact Details",
                    "components": [
                        {"name": "name_field", "type": "TextField", "title": "Your Name"},
                        {"name": "email_field", "type": "EmailAddressField", "title": "Email"},
                        {"name": "html_content", "type": "Html", "title": "Info Text"},  # Should be filtered
                    ],
                },
                {
                    "path": "/summary",  # Should be skipped
                    "title": "Summary",
                    "components": [{"name": "summary_field", "type": "TextField", "title": "Summary"}],
                },
            ]
        }

        mock_section = Mock()
        mock_section.name_in_apply_json = {"en": "Application Details"}
        mock_section.forms = [mock_form]

        return [mock_section]

    @patch("app.export_config.generate_assessment_config.copy.deepcopy")
    @patch("app.export_config.generate_assessment_config.db")
    @patch("app.export_config.generate_assessment_config.helpers")
    @patch("app.export_config.generate_assessment_config.form_json_to_assessment_display_types")
    @patch("app.export_config.generate_assessment_config.human_to_kebab_case")
    def test_basic_config_generation(
        self, mock_kebab, mock_display_types, mock_helpers, mock_db, mock_deepcopy, configs, mock_form_data
    ):
        fund_config, round_config = configs
        mock_kebab.side_effect = lambda x: x.lower().replace(" ", "-")
        mock_display_types.get.return_value = "text"

        # Setup database query
        mock_db.session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_form_data

        # Setup template - this is the key fix
        mock_template = Mock()
        mock_template.substitute.return_value = "generated_config"
        mock_deepcopy.return_value = mock_template

        # Run function
        generate_assessment_config_for_round(fund_config, round_config, "/output")

        # Verify template was called with correct parameters
        mock_template.substitute.assert_called_once()
        call_args = mock_template.substitute.call_args[1]
        assert call_args["fund_round"] == "TEST_FUNDROUND_1"
        assert call_args["fund_id"] == "fund-123"
        assert call_args["round_id"] == "round-456"

        # Verify config was written
        mock_helpers.write_config.assert_called_once()

    @patch("app.export_config.generate_assessment_config.copy.deepcopy")
    @patch("app.export_config.generate_assessment_config.db")
    @patch("app.export_config.generate_assessment_config.helpers")
    @patch("app.export_config.generate_assessment_config.form_json_to_assessment_display_types")
    @patch("app.export_config.generate_assessment_config.human_to_kebab_case")
    def test_unscored_data_structure(
        self, mock_kebab, mock_display_types, mock_helpers, mock_db, mock_deepcopy, configs, mock_form_data
    ):
        fund_config, round_config = configs
        mock_kebab.side_effect = lambda x: x.lower().replace(" ", "-")
        mock_display_types.get.return_value = "text"

        mock_db.session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_form_data

        mock_template = Mock()
        mock_template.substitute.return_value = "config"
        mock_deepcopy.return_value = mock_template

        generate_assessment_config_for_round(fund_config, round_config, "/output")

        # Check the unscored data structure
        call_args = mock_template.substitute.call_args[1]
        unscored = json.loads(call_args["unscored"])

        # Should have one criteria (section)
        assert len(unscored) == 1
        criteria = unscored[0]
        assert criteria["name"] == "Application Details"

        # Should have one sub_criteria (form)
        assert len(criteria["sub_criteria"]) == 1
        sub_criteria = criteria["sub_criteria"][0]
        assert sub_criteria["name"] == "Test Form"

        # Should have one theme (page, summary skipped)
        assert len(sub_criteria["themes"]) == 1
        theme = sub_criteria["themes"][0]
        assert theme["name"] == "Contact Details"

        # Should have 2 answers (HTML component filtered out)
        assert len(theme["answers"]) == 2

        # Check answer structure
        answer = theme["answers"][0]
        assert answer["field_id"] == "name_field"
        assert answer["form_name"] == "test-form"
        assert answer["field_type"] == "textField"  # First letter lowercase
        assert answer["question"] == "Your Name"

    @patch("app.export_config.generate_assessment_config.copy.deepcopy")
    @patch("app.export_config.generate_assessment_config.db")
    @patch("app.export_config.generate_assessment_config.helpers")
    @patch("app.export_config.generate_assessment_config.form_json_to_assessment_display_types")
    @patch("app.export_config.generate_assessment_config.human_to_kebab_case")
    def test_readonly_components_filtered(
        self, mock_kebab, mock_display_types, mock_helpers, mock_db, mock_deepcopy, configs
    ):
        fund_config, round_config = configs
        mock_kebab.side_effect = lambda x: x.lower().replace(" ", "-")
        mock_display_types.get.return_value = "text"

        # Create form with only readonly components
        mock_form = Mock()
        mock_form.runner_publish_name = "readonly-form"
        mock_form.name_in_apply_json = {"en": "Readonly Form"}
        mock_form.form_json = {
            "pages": [
                {
                    "path": "/readonly",
                    "title": "Readonly Page",
                    "components": [
                        {"name": "html_field", "type": "Html", "title": "HTML"},
                        {"name": "para_field", "type": "Para", "title": "Paragraph"},
                    ],
                }
            ]
        }

        mock_section = Mock()
        mock_section.name_in_apply_json = {"en": "Test"}
        mock_section.forms = [mock_form]

        mock_db.session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_section]

        mock_template = Mock()
        mock_template.substitute.return_value = "config"
        mock_deepcopy.return_value = mock_template

        generate_assessment_config_for_round(fund_config, round_config, "/output")

        # Should have no answers since all components are readonly
        call_args = mock_template.substitute.call_args[1]
        unscored = json.loads(call_args["unscored"])
        answers = unscored[0]["sub_criteria"][0]["themes"][0]["answers"]
        assert len(answers) == 0

    @patch("app.export_config.generate_assessment_config.copy.deepcopy")
    @patch("app.export_config.generate_assessment_config.db")
    @patch("app.export_config.generate_assessment_config.helpers")
    @patch("app.export_config.generate_assessment_config.form_json_to_assessment_display_types")
    @patch("app.export_config.generate_assessment_config.human_to_kebab_case")
    def test_empty_sections(self, mock_kebab, mock_display_types, mock_helpers, mock_db, mock_deepcopy, configs):
        fund_config, round_config = configs
        mock_kebab.side_effect = lambda x: x.lower().replace(" ", "-")

        # No sections
        mock_db.session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        mock_template = Mock()
        mock_template.substitute.return_value = "config"
        mock_deepcopy.return_value = mock_template

        generate_assessment_config_for_round(fund_config, round_config, "/output")

        # Should have empty unscored list
        call_args = mock_template.substitute.call_args[1]
        unscored = json.loads(call_args["unscored"])
        assert unscored == []
