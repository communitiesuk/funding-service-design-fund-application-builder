import os
from string import Template

from app.shared.helpers import convert_to_dict
from config import Config


def human_to_kebab_case(string: str) -> str | None:
    return string.replace(" ", "-").strip().lower() if string else None


def human_to_snake_case(string: str) -> str | None:
    return string.replace(" ", "_").strip().lower() if string else None


def write_config(config, filename, round_short_name, config_type, base_output_dir=None):
    # Get the directory of the current file

    # Construct the path to the output directory relative to this file's location
    if base_output_dir is None:
        base_output_dir = Config.TEMP_FILE_PATH / round_short_name

    if config_type == "form_json":
        output_dir = base_output_dir / "form_runner"
        content_to_write = config
        # Ensure the filename ends with .json
        if not filename.endswith(".json"):
            if any(
                filename.endswith(ext) for ext in [".py", ".html", ".txt", ".csv"]
            ):  # Add other file types as needed
                raise ValueError(f"Invalid file type for form_json: {filename}")
            filename = f"{filename}.json"
        file_path = output_dir / f"{human_to_kebab_case(filename)}"
    elif config_type == "python_file":
        output_dir = base_output_dir / "fund_store"
        config_dict = convert_to_dict(config)  # Convert config to dict for non-JSON types
        content_to_write = "LOADER_CONFIG="
        content_to_write += str(config_dict)
        file_path = output_dir / f"{human_to_snake_case(filename)}.py"
    elif config_type == "html":
        output_dir = base_output_dir / "html"
        content_to_write = config
        file_path = output_dir / f"{filename}_all_questions_en.html"

    elif config_type == "assessment":
        output_dir = base_output_dir / "assessment_store"
        content_to_write = str(config)
        file_path = output_dir / f"{human_to_snake_case(filename)}.py"

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write the content to the file
    with open(file_path, "w") as f:
        if config_type == "form_json":
            f.write(content_to_write)  # Write JSON string directly
        elif config_type == "python_file":
            print(content_to_write, file=f)  # Print the dictionary for non-JSON types
        elif config_type == "html":
            f.write(content_to_write)
        elif config_type == "assessment":
            f.write(content_to_write)


assess_output = Template(
    """
{
    "fund_round_to_assessment_mapping": {
        "schema_id": "${fund_round}_assessment",
        "unscored_sections": ${unscored}
    },
    "fund_round_mapping_config": {
        "${fund_round}": {
            "fund_id": "${fund_id}",
            "round_id": "${round_id}",
            "type_of_application": "${fund_short_name}",
        },
    },
}
"""
)
