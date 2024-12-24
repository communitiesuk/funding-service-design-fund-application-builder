from flask import Flask, render_template
from fsd_utils import init_sentry
from fsd_utils.authentication.decorators import SupportedApp, check_internal_user, login_required
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from app.blueprints.application.routes import application_bp
from app.blueprints.fund.routes import fund_bp
from app.blueprints.fund_builder.routes import build_fund_bp
from app.blueprints.round.routes import round_bp
from app.blueprints.template.routes import template_bp

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
    flask_app.register_blueprint(build_fund_bp)
    flask_app.register_blueprint(fund_bp)
    flask_app.register_blueprint(round_bp)
    flask_app.register_blueprint(application_bp)
    flask_app.register_blueprint(template_bp)

    protect_private_routes(flask_app)

    flask_app.config.from_object("config.Config")

    flask_app.static_folder = "app/static/dist"

    from app.db import db, migrate

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
