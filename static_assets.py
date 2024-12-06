"""Compile static assets."""

from os import path

from flask import Flask
from flask_assets import Environment


def init_assets(app=None, auto_build=False, static_folder="app/static/dist"):
    app = app or Flask(__name__)
    # app.static_folder = static_folder  # config.Config.STATIC_FOLDER
    # app.static_url_path = config.Config.STATIC_URL_PATH
    with app.app_context():
        env = Environment(app)
        env.load_path = [path.join(path.dirname(__file__), "static/src")]
        # env.set_directory(env_directory)
        # App Engine doesn't support automatic rebuilding.
        env.auto_build = auto_build
        # This file needs to be shipped with your code.
        env.manifest = "file"

        bundles = []

        return bundles


def build_bundles(static_folder="app/static/dist"):
    bundles = init_assets(static_folder=static_folder)
    for bundle in bundles:
        bundle.build()


if __name__ == "__main__":
    build_bundles()
