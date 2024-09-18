from flask import Flask
from flask_assets import Environment
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader

import static_assets
from app.blueprints.dev.routes import dev_bp
from app.blueprints.fund_builder.routes import build_fund_bp
from app.blueprints.self_serve.routes import self_serve_bp
from app.blueprints.templates.routes import template_bp
from app.db.models import Fund  # noqa:F401
from app.db.models import Round  # noqa:F401


def create_app() -> Flask:

    flask_app = Flask("__name__", static_url_path="/assets")
    flask_app.register_blueprint(self_serve_bp)
    flask_app.register_blueprint(dev_bp)
    flask_app.register_blueprint(build_fund_bp)
    flask_app.register_blueprint(template_bp)

    flask_app.config.from_object("config.Config")

    flask_app.static_folder = "app/static/dist"

    from app.db import db
    from app.db import migrate

    # Bind SQLAlchemy ORM to Flask app
    db.init_app(flask_app)
    # Bind Flask-Migrate db utilities to Flask app
    migrate.init_app(
        flask_app,
        db,
        directory="app/db/migrations",
        render_as_batch=True,
        compare_type=True,
        compare_server_default=True,
    )

    # Bundle and compile assets
    assets = Environment()
    assets.init_app(flask_app)

    static_assets.init_assets(
        flask_app,
        auto_build=True,
        static_folder="app/static/dist",
    )

    flask_app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
        ]
    )
    flask_app.jinja_env.add_extension("jinja2.ext.do")

    return flask_app


app = create_app()
