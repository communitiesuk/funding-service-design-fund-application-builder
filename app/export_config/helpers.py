import os

import jsonschema
from flask import current_app
from jsonschema import validate

from app.blueprints.self_serve.routes import human_to_kebab_case
from app.blueprints.self_serve.routes import human_to_snake_case
from app.shared.helpers import convert_to_dict
from config import Config


def write_config(config, filename, round_short_name, config_type):
    # Get the directory of the current file

    # Construct the path to the output directory relative to this file's location
    base_output_dir = Config.TEMP_FILE_PATH / round_short_name

    if config_type == "form_json":
        output_dir = base_output_dir / "form_runner"
        content_to_write = config
        # Ensure the filename ends with .json
        if not filename.endswith('.json'):
            if any(filename.endswith(ext) for ext in ['.py', '.html', '.txt', '.csv']):  # Add other file types as needed
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


# Function to validate JSON data against the schema
def validate_json(data, schema):
    try:
        validate(instance=data, schema=schema)
        current_app.logger.info("Given JSON data is valid")
        return True
    except jsonschema.exceptions.ValidationError as err:
        current_app.logger.error("Given JSON data is invalid")
        current_app.logger.error(err)
        return False
