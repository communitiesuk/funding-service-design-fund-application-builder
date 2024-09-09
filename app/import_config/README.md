# FAB Config Import

This directory contains the scripts to import the FAB configuration files.

The import configuration file is a form JSON that has been produced by the form designer. The forms are ingested into the FAB database as baseline templates. These templates can then be cloned into applications were users can optionally perform light touch editing of the contained pages and components.

To import a form JSON, each file should be places in the following directory:

    app/import_config/files_to_import/ ** ({formname}.json)

The import can be triggered manually by running the following command:

    python app/import_config/load_form_json.py
