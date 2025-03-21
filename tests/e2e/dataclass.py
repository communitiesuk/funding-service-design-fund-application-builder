from dataclasses import dataclass


@dataclass
class Account:
    email_address: str
    roles: list[str]


@dataclass
class FabDomains:
    fab_url: str
    cookie_domain: str
    environment: str
