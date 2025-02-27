from flask import request, session

from app.blueprints.application.routes import application_bp, section
from app.blueprints.fund.routes import fund_bp, view_all_funds
from app.blueprints.index.routes import dashboard, go_back, index_bp
from app.blueprints.round.routes import round_bp, view_all_rounds
from app.blueprints.template.routes import template_bp, view_templates


class PageTracker:
    def __init__(self):
        self.tracked_blueprints = {
            template_bp.name,
            index_bp.name,
            application_bp.name,
            fund_bp.name,
            round_bp.name
        }
        self.ignore_endpoints = {f'{application_bp.name}.{section.__name__}',
                                 f'{index_bp.name}.{go_back.__name__}'}
        self.reset_endpoints = {
            f'{index_bp.name}.{dashboard.__name__}',
            f'{fund_bp.name}.{view_all_funds.__name__}',
            f'{round_bp.name}.{view_all_rounds.__name__}',
            f'{template_bp.name}.{view_templates.__name__}'
        }

    @staticmethod
    def initialize_session():
        """Initialize session variables if not already present."""
        if 'visited_pages' not in session:
            session['visited_pages'] = []

    def should_track(self, endpoint):
        """Check if the page should be tracked."""
        if endpoint is None:
            return False
        return any(bp in endpoint for bp in self.tracked_blueprints) and endpoint not in self.ignore_endpoints

    def reset_session(self, endpoint, page):
        """Reset session if the endpoint is in the reset list."""
        if endpoint in self.reset_endpoints and page:
            session["visited_pages"] = [page]
            session.modified = True

    def track_page(self, endpoint, page):
        """Track the page if the conditions are met."""
        if self.should_track(endpoint) and page:
            visited_pages = session["visited_pages"]

            # Check if the endpoint is already in the visited pages
            for i, visited_page in enumerate(visited_pages):
                if visited_page["endpoint"] == endpoint:
                    # Remove all entries after this one
                    session["visited_pages"] = visited_pages[:i + 1]
                    session.modified = True
                    return

            # If the endpoint is not found, append it
            visited_pages.append(page)
            session.modified = True

    def process_request(self, endpoint):
        """Process the page tracking logic."""
        self.initialize_session()
        page = {"endpoint": endpoint, "view_args": request.view_args or {}, "query_params": request.args.to_dict()}
        self.track_page(endpoint, page)
        self.reset_session(endpoint, page)
