from flask import Flask
from flask import render_template
from fsd_utils import init_sentry
from fsd_utils.authentication.decorators import SupportedApp
from fsd_utils.authentication.decorators import check_internal_user
from fsd_utils.authentication.decorators import login_required
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader

from app.blueprints.fund_builder.routes import build_fund_bp
from app.blueprints.self_serve.routes import self_serve_bp
from app.blueprints.templates.routes import template_bp

PUBLIC_ROUTES = [
    "static",
    "build_fund_bp.index",
    "build_fund_bp.login",
]


def protect_private_routes(flask_app: Flask) -> Flask:
    for endpoint, view_func in flask_app.view_functions.items():
        if endpoint in PUBLIC_ROUTES:
            continue
        flask_app.view_functions[endpoint] = login_required(
            check_internal_user(view_func), return_app=SupportedApp.FUND_APPLICATION_BUILDER
        )
    return flask_app


def create_app() -> Flask:
    init_sentry()
    flask_app = Flask("__name__", static_url_path="/assets")
    flask_app.register_blueprint(self_serve_bp)
    flask_app.register_blueprint(build_fund_bp)
    flask_app.register_blueprint(template_bp)

    protect_private_routes(flask_app)

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

    # Initialise logging
    logging.init_app(flask_app)

    flask_app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
        ]
    )
    flask_app.jinja_env.add_extension("jinja2.ext.do")

    @flask_app.errorhandler(403)
    def forbidden_error(error):
        return render_template("403.html"), 403

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())

    return flask_app


app = create_app()
