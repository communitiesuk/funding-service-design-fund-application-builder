import glob
import os
import shutil
import urllib.request
import zipfile


def copy_static_files(src_subdir, dist_subdir, file_pattern="*.*"):
    """Generic function to copy static files from src to dist"""
    src_dir = f"./app/static/src/{src_subdir}"
    dist_dir = f"./app/static/dist/{src_subdir}"

    if os.path.exists(src_dir):
        os.makedirs(dist_dir, exist_ok=True)
        for file in glob.glob(os.path.join(src_dir, file_pattern)):
            print(f"Copying {file} to {dist_dir}")
            shutil.copy2(file, dist_dir)


def build_govuk_assets(static_dist_root="app/static/dist"):
    DIST_ROOT = "./" + static_dist_root
    GOVUK_DIR = "/govuk-frontend"
    GOVUK_URL = "https://github.com/alphagov/govuk-frontend/releases/download/v5.6.0/release-v5.6.0.zip"
    ZIP_FILE = "./govuk_frontend.zip"
    DIST_PATH = DIST_ROOT + GOVUK_DIR
    ASSETS_DIR = "/assets"
    ASSETS_PATH = DIST_PATH + ASSETS_DIR

    # Checks if GovUK Frontend Assets already built
    if os.path.exists(DIST_PATH):
        print("GovUK Frontend assets already built. If you require a rebuild manually run build.build_govuk_assets")
        return True

    # Download zips from GOVUK_URL
    # There is a known problem on Mac where one must manually
    # run the script "Install Certificates.command" found
    # in the python application folder for this to work.

    print("Downloading static file zip.")
    urllib.request.urlretrieve(GOVUK_URL, ZIP_FILE)  # nosec

    # Attempts to delete the old files, states if
    # one doesn't exist.

    print("Deleting old " + DIST_PATH)
    try:
        shutil.rmtree(DIST_PATH)
    except FileNotFoundError:
        print("No old " + DIST_PATH + " to remove.")

    # Extract the previously downloaded zip to DIST_PATH

    print("Unzipping file to " + DIST_PATH + "...")
    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(DIST_PATH)

    # Move files from ASSETS_PATH to DIST_PATH

    print("Moving files from " + ASSETS_PATH + " to " + DIST_PATH)
    for file_to_move in os.listdir(ASSETS_PATH):
        shutil.move("/".join([ASSETS_PATH, file_to_move]), DIST_PATH)

    # We are using pre-compiled GOV.UK Frontend at the moment, which bakes in some expected URL paths for certain
    # assets. So here we massage some files into the correct place.
    print("Copying images and fonts to /static for hard-coded CSS in GOV.UK Frontend")
    shutil.copytree("app/static/dist/govuk-frontend/images", "app/static/dist/images")
    shutil.copytree("app/static/dist/govuk-frontend/fonts", "app/static/dist/fonts")
    shutil.copy("app/static/dist/govuk-frontend/manifest.json", "app/static/dist/manifest.json")

    # Delete temp files
    print("Deleting " + ASSETS_PATH)
    shutil.rmtree(ASSETS_PATH)
    os.remove(ZIP_FILE)


def build_all(static_dist_root="app/static/dist", remove_existing=False):
    if remove_existing:
        relative_dist_root = "./" + static_dist_root
        if os.path.exists(relative_dist_root):
            shutil.rmtree(relative_dist_root)
    build_govuk_assets(static_dist_root=static_dist_root)
    copy_static_files("styles", "styles", "*.css")
    copy_static_files("js", "js", "*.js")


if __name__ == "__main__":
    build_all(remove_existing=True)
