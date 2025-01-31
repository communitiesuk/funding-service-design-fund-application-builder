import uuid

from flask import Flask, render_template, session, request
from flask_talisman import Talisman
from fsd_utils import init_sentry
from fsd_utils.authentication.decorators import SupportedApp, check_internal_user, login_required
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.logging import logging
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from app.blueprints.application.routes import application_bp
from app.blueprints.fund.routes import fund_bp
from app.blueprints.index.routes import index_bp
from app.blueprints.round.routes import round_bp
from app.blueprints.template.routes import template_bp
from config import Config

PUBLIC_ROUTES = [
    "static",
    "index_bp.index",
    "index_bp.login",
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
    flask_app.register_blueprint(index_bp)
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

    if flask_app.config["FLASK_ENV"] == "development":
        from flask_debugtoolbar import DebugToolbarExtension

        DebugToolbarExtension(flask_app)

    # Configure application security with Talisman
    Talisman(flask_app, **Config.TALISMAN_SETTINGS)

    # Initialise logging
    logging.init_app(flask_app)

    flask_app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PackageLoader("govuk_frontend_ext"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )
    flask_app.jinja_env.add_extension("jinja2.ext.do")

    WTFormsHelpers(flask_app)

    @flask_app.errorhandler(403)
    def forbidden_error(error):
        return render_template("403.html"), 403

    @flask_app.before_request
    def track_pages():
        # Initialize the visited pages list if not already
        if 'visited_pages' not in session:
            session['visited_pages'] = []
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        endpoint = request.endpoint
        if not endpoint or "go_back" in endpoint:
            return

        tracked_blueprints = {"template_bp", "index_bp", "application_bp", "fund_bp", "round_bp"}
        ignore_endpoints = {"application_bp.build_application"}
        reset_endpoints = {
            "index_bp.dashboard", "fund_bp.view_all_funds",
            "round_bp.view_all_rounds", "template_bp.view_templates"
        }

        page = None
        if any(bp in endpoint for bp in tracked_blueprints) and endpoint not in ignore_endpoints:
            page = {"endpoint": endpoint, "view_args": request.view_args or {}, "query_params": request.args.to_dict()}
            if not session["visited_pages"] or session["visited_pages"][-1]["endpoint"] != endpoint:
                session["visited_pages"].append(page)
                session.modified = True

        # reset session based on the above endpoints
        if endpoint in reset_endpoints and page:
            session["visited_pages"] = [page]
        session.modified = True

    @flask_app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500

    health = Healthcheck(flask_app)
    health.add_check(FlaskRunningChecker())

    return flask_app


app = create_app()
