import base64
import json
import subprocess
from pathlib import Path
from typing import Literal, Protocol

import boto3
from playwright.sync_api import HttpCredentials


class EndToEndTestSecrets(Protocol):
    @property
    def HTTP_BASIC_AUTH(self) -> HttpCredentials | None: ...

    @property
    def JWT_SIGNING_KEY(self) -> str | None: ...


class LocalEndToEndSecrets:
    @property
    def HTTP_BASIC_AUTH(self) -> None:
        return None

    @property
    def JWT_SIGNING_KEY(self) -> str:
        _test_private_key_path = (
            str(Path(__file__).parent.parent) + "/e2e/keys/rsa256/private.pem"  # pragma: allowlist secret
        )
        with open(_test_private_key_path, mode="r") as private_key_file:
            rsa256_private_key = private_key_file.read()

        return rsa256_private_key


class AWSEndToEndSecrets:
    def __init__(self, e2e_env: Literal["dev", "test"], e2e_aws_vault_profile: str | None):
        self.e2e_env = e2e_env
        self.e2e_aws_vault_profile = e2e_aws_vault_profile

        if self.e2e_env == "prod":  # type: ignore[comparison-overlap]
            # It shouldn't be possible to set e2e_env to `prod` based on current setup; this is a safeguard against it
            # being added in the future without thinking about this fixture. When it comes to prod secrets, remember:
            #   keep it secret; keep it safe.
            raise ValueError("Refusing to init against prod environment because it would read production secrets")

    def _read_aws_parameter_store_value(self, parameter):
        # This flow is used to collect secrets when running tests *from* your local machine
        if self.e2e_aws_vault_profile:
            value = json.loads(
                subprocess.check_output(
                    [
                        "aws-vault",
                        "exec",
                        self.e2e_aws_vault_profile,
                        "--",
                        "aws",
                        "ssm",
                        "get-parameter",
                        "--name",
                        parameter,
                        "--with-decryption",
                    ],
                ).decode()
            )["Parameter"]["Value"]

        # This flow is used when running tests *in* CI/CD, where AWS credentials are available from OIDC auth
        else:
            ssm_client = boto3.client("ssm")
            value = ssm_client.get_parameter(Name=parameter, WithDecryption=True)["Parameter"]["Value"]

        return value

    @property
    def HTTP_BASIC_AUTH(self) -> HttpCredentials:
        return {
            "username": self._read_aws_parameter_store_value(
                f"/copilot/pre-award/{self.e2e_env}/secrets/BASIC_AUTH_USERNAME"
            ),
            "password": self._read_aws_parameter_store_value(
                f"/copilot/pre-award/{self.e2e_env}/secrets/BASIC_AUTH_PASSWORD"
            ),
        }

    @property
    def JWT_SIGNING_KEY(self) -> str:
        base64_value = self._read_aws_parameter_store_value(
            f"/copilot/pre-award/{self.e2e_env}/secrets/RSA256_PRIVATE_KEY_BASE64"
        )
        return base64.b64decode(base64_value).decode()
