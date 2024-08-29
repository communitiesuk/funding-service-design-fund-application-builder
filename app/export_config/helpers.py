import os
from datetime import date

import jsonschema
from flask import current_app
from jsonschema import validate

from app.blueprints.self_serve.routes import human_to_kebab_case
from app.blueprints.self_serve.routes import human_to_snake_case
from app.shared.helpers import convert_to_dict


def write_config(config, filename, round_short_name, config_type):
    # Get the directory of the current file
    current_dir = os.path.dirname(__file__)

    # Construct the path to the output directory relative to this file's location
    base_output_dir = os.path.join(current_dir, f"output/{round_short_name}/")

    if config_type == "form_json":
        output_dir = os.path.join(base_output_dir, "form_runner/")
        content_to_write = config
        file_path = os.path.join(output_dir, f"{human_to_kebab_case(filename)}.json")
    elif config_type == "python_file":
        output_dir = os.path.join(base_output_dir, "fund_store/")
        config_dict = convert_to_dict(config)  # Convert config to dict for non-JSON types
        content_to_write = str(config_dict)
        file_path = os.path.join(output_dir, f"{human_to_snake_case(filename)}_{date.today().strftime('%d-%m-%Y')}.py")
    elif config_type == "html":
        output_dir = os.path.join(base_output_dir, "html/")
        content_to_write = config
        file_path = os.path.join(output_dir, f"{filename}.html")

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
