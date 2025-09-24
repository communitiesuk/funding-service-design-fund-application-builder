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
    def mock_published_forms(self):
        """Default published forms for most tests"""
        mock_form = Mock()
        mock_form.url_path = "test-form"
        mock_form.display_name = "Test Form"
        return [mock_form]

    @pytest.fixture
    def mock_api_service(self, mock_published_forms):
        """Mock FormStoreAPIService with default published forms"""
        mock_service = Mock()
        mock_service.get_published_forms.return_value = mock_published_forms
        return mock_service

    @pytest.fixture
    def mock_form_data(self):
        mock_form = Mock()
        mock_form.runner_publish_name = "test-form"
        mock_form.url_path = "test-form"
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

    @pytest.fixture
    def common_patches(self):
        """Common patches that most tests need"""
        with (
            patch("app.export_config.generate_assessment_config.copy.deepcopy") as mock_deepcopy,
            patch("app.export_config.generate_assessment_config.db") as mock_db,
            patch("app.export_config.generate_assessment_config.helpers") as mock_helpers,
            patch(
                "app.export_config.generate_assessment_config.form_json_to_assessment_display_types"
            ) as mock_display_types,
            patch("app.export_config.generate_assessment_config.human_to_kebab_case") as mock_kebab,
            patch("app.export_config.generate_assessment_config.FormStoreAPIService") as mock_api_service_class,
        ):
            # Setup common behavior
            mock_kebab.side_effect = lambda x: x.lower().replace(" ", "-")
            mock_display_types.get.return_value = "text"

            # Setup mock API service
            mock_api_service = Mock()
            mock_api_service.get_display_name_from_url_path.return_value = "Test Form"
            mock_api_service_class.return_value = mock_api_service

            mock_template = Mock()
            mock_template.substitute.return_value = "generated_config"
            mock_deepcopy.return_value = mock_template

            yield {
                "deepcopy": mock_deepcopy,
                "db": mock_db,
                "helpers": mock_helpers,
                "display_types": mock_display_types,
                "kebab": mock_kebab,
                "api_service_class": mock_api_service_class,
                "api_service": mock_api_service,
                "template": mock_template,
            }

    def test_basic_config_generation(self, configs, mock_form_data, common_patches):
        fund_config, round_config = configs

        # Setup database query
        common_patches[
            "db"
        ].session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_form_data

        # Run function
        generate_assessment_config_for_round(fund_config, round_config, "/output")

        # Verify template was called with correct parameters
        common_patches["template"].substitute.assert_called_once()
        call_args = common_patches["template"].substitute.call_args[1]
        assert call_args["fund_round"] == "TEST_FUNDROUND_1"
        assert call_args["fund_id"] == "fund-123"
        assert call_args["round_id"] == "round-456"

        # Verify config was written
        common_patches["helpers"].write_config.assert_called_once()

    def test_unscored_data_structure(self, configs, mock_form_data, common_patches):
        fund_config, round_config = configs

        common_patches[
            "db"
        ].session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_form_data

        generate_assessment_config_for_round(fund_config, round_config, "/output")

        # Check the unscored data structure
        call_args = common_patches["template"].substitute.call_args[1]
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

    def test_readonly_components_filtered(self, configs, common_patches):
        fund_config, round_config = configs

        # Create form with only readonly components
        mock_form = Mock()
        mock_form.runner_publish_name = "readonly-form"
        mock_form.url_path = "readonly-form"
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

        # Set up API service to return display name for this form
        common_patches["api_service"].get_display_name_from_url_path.return_value = "Readonly Form"

        common_patches["db"].session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_section
        ]

        generate_assessment_config_for_round(fund_config, round_config, "/output")

        # Should have no answers since all components are readonly
        call_args = common_patches["template"].substitute.call_args[1]
        unscored = json.loads(call_args["unscored"])
        answers = unscored[0]["sub_criteria"][0]["themes"][0]["answers"]
        assert len(answers) == 0

    def test_empty_sections(self, configs, common_patches):
        fund_config, round_config = configs

        # No sections
        common_patches["db"].session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        generate_assessment_config_for_round(fund_config, round_config, "/output")

        # Should have empty unscored list
        call_args = common_patches["template"].substitute.call_args[1]
        unscored = json.loads(call_args["unscored"])
        assert unscored == []
