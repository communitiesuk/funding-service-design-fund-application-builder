# FAB Config Output

This directory contains the scripts and output required to generate the FAB configuration files.

## Scripts
### Generate fund round configuration
    Generates configuration for a specific funding round.

    This function orchestrates the generation of various configurations needed for a funding round.
    It calls three specific functions in sequence to generate the fund configuration, round configuration,
    and application display configuration for the given round ID.

    Args:
        round_id (str): The unique identifier for the funding round.

    The functions called within this function are:
    - generate_fund_config: Generates the fund configuration for the given round ID.
    - generate_round_config: Generates the round configuration for the given round ID.
    - generate_application_display_config: Generates the application display configuration for the given round ID.

### Generate round form JSONs
    Generates JSON configurations for all forms associated with a given funding round.

    This function iterates through all sections of a specified funding round, and for each form
    within those sections, it generates a JSON configuration. These configurations are then written
    to files named after the forms, organized by the round's short name.

    Args:
        round_id (str): The unique identifier for the funding round.

    The generated files are named after the form names and are stored in a directory
    corresponding to the round's short name.

### Generate round html
    Generates an HTML representation for a specific funding round.

    This function creates an HTML document that represents all the sections and forms
    associated with a given funding round. It retrieves the round and its related fund
    information, iterates through each section of the round to collect form data, and
    then generates HTML content based on this data.

    Args:
        round_id (str): The unique identifier for the funding round.

    The generated HTML is intended to provide a comprehensive overview of the round,
    including details of each section and form, for printing or web display purposes.

## Running the scripts
To run the scripts, execute the following commands:

```bash
inv generate-fund-and-round-config {roundid}

inv generate-round-form-jsons {roundid}

inv generate-round-html {roundid}
```

## Output
The scripts generate the following output file structure:
```plaintext
app/
    - export/
        - config_generator/
            -- scripts[.py]
            - output/
                - round_short_name/
                - form_runner/
                    -- form_name.json
                - fund_store/
                    -- fund_config.py
                    -- round_config.py
                    -- sections_config.py
                - html/
                    -- full_aplication.html
```

<!-- TODO: Is this now covered by cloning? >> -->
<!-- # SPIKE to look at Question Bank and answer config_reuse -->
<!-- By storing some reusable configuration outside the form jsons, we can allow parts of forms to be generated from minimal input information - making it more feasible for less technical colleagues to create this input information, or for it to be generated by a UI.

Creating forms from reusable questions means the answers to those questions will line up between applications, so we can more easily allow applicants to take information from one application and reuse in another.

Having reusable questions also means we can have reusable assessment config - eg. the organisation information can be reused in un-scored general information sections without duplicating the config.

## Reusable configuration
[Components](./config/components_to_reuse.py) Configuration for individual components (fields). Structure is as in the form json, except for conditions which are simplified
[Pages](./config/pages_to_reuse.py) Configuration for pages that can be inserted into forms. Basically each page is a list of component IDs that exist in `components_to_reuse.py` above.
[Sub Pages](./config/sub_pages_to_reuse.py) Contains full form json info for some pages that are constant when reused, eg. the summary page. But also ones that are needed for sub flows based on conditions - eg. the 'what alternative names does your org use' page is in here, as it will always be required if you add the component `reuse_organisation_other_names_yes_no`
[Assessment Themes](./config/themes_to_reuse.py) Specifies themes that can be reused across assessments, basically a list of the components in each theme. These component names are the same as in `components_to_reuse.py`

## Example inputs - Forms
These are examples of the inputs required from a fund to create forms based on reusable components. Once the form json is generated, it can always be edited to add non-reusable components/pages as well.
[Org Info Basic](./test_data/in/org-info_basic_name_address.json) Just asks for organisation name and address
[Org info with alternative names](./test_data/in/org-info_alt_name_address.json) As above but allows alternative names
[Full organisation info](./test_data/in/org-info_all.json) Uses all the components configured as part of the POC - org name, address, alternative names, purpose and web links

## Example inputs - Assessment
Example of input to generate assessment configuration for the `Full Organisation Info` example form above
[Un-scored Full org info](./test_data/in/assmnt_unscored.json) Lists the themes within each sub-criteria for the assessment sections

# Steps to generate form json
1. Create an input file, as per [example inputs](#example-inputs---forms) specifying the pages you want in your form
1. Execute the form generation script: `python -m config_reuse.generate_form` and complete the command prompts to generate the json from the input

# Steps to generate assessment config for a set of questions
1. Create an input file, as per [example inputs](#example-inputs---assessment) specifying the layout of themes etc that you need
1. Generate field info for the forms you are using - atm run `test_generate_assessment_fields_for_testing` in `test_generate_all_questions.py` in fund-store.
1. Run the assessment config generation script: `python -m config_reuse.generate_assessment_config` and answer the prompts, point it to the input file you created and the generated field info from the previous step. -->
