def json_import(data, template_name, filename):
    from app.import_config.load_form_json import load_json_from_file

    return load_json_from_file(data, template_name, filename)
