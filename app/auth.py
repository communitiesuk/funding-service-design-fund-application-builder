from functools import wraps

from flask import abort, current_app, g
from fsd_utils.authentication.config import InternalDomain


def check_allowed_domains(func):
    """
    Checks if the authenticated user's email domain is allowed.
    Combines the internal domains from fsd_utils with additional domains from ALLOWED_DOMAINS.
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        internal_domains = tuple(k.value for k in InternalDomain)
        fab_domains_str = current_app.config.get("ALLOWED_DOMAINS", "")
        fab_domains = [f"@{domain.strip()}" for domain in fab_domains_str.split(",") if domain.strip()]
        all_allowed_domains = internal_domains + tuple(fab_domains)
        is_allowed_domain = any(g.user.email.endswith(domain) for domain in all_allowed_domains)
        if is_allowed_domain:
            return func(*args, **kwargs)
        else:
            abort(403)

    return decorated
