import shutil

from config import Config


def create_export_zip(directory_to_zip, zip_file_name, random_post_fix) -> str:
    # Output zip file path (temporary)
    output_zip_path = Config.TEMP_FILE_PATH / f"{zip_file_name}-{random_post_fix}"

    # Create a zip archive of the directory
    shutil.make_archive(base_name=output_zip_path, format="zip", root_dir=directory_to_zip)
    return f"{output_zip_path}.zip"
