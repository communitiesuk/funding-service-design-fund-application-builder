# Python E2E tests

These are FAB E2E tests written using [Playwright](https://playwright.dev/python/).

# Pre Reqs

- Playwright and other dependencies installed:
    - Run `uv run playwright install --with-deps chromium` (this is a one-time setup step and may take a little while)
- If running against your local machine, you will need the fab services up and running - see
  the [docker runner](https://github.com/communitiesuk/funding-service-design-docker-runner) for details on this.
- If running from your local machine against `dev` or `test`, you will also need
  `aws-vault` [installed](https://github.com/99designs/aws-vault/blob/master/README.md)
  and [setup](https://mhclgdigital.atlassian.net/wiki/spaces/FS/pages/5241813/Using+AWS+Vault+SSO#Install-AWS-Vault)
  with profiles for your target environment.

# Running

## Locally—Against your local machine

- These tests can be run the same way you normally run `pytest` - either from the command line or using an IDE
  extension.

```
    uv run pytest --e2e
```

- You can optionally add the `headed` switch to see the browser window while the tests run

```
    uv run pytest --e2e --headed
```

## Locally - Against dev or test

- To run against a non-local environment, pass the environment you want to target, and the aws-vault profile name to
  use, and run with pytest as normal:

```
    uv run pytest --e2e --e2e-env dev --e2e-aws-vault-profile fsd-dev
```

In this case, `fsd-dev` is the name of the profile in the aws-vault config file (~/.aws/config):

```
    [profile fsd-dev]
    region=eu-west-2
    source_profile=XXXXX
    role_arn=arn:aws:iam::123123123123:role/developer
    mfa_serial=arn:aws:iam::123123123123:mfa/user.name
```

## Parallel test runs

By default the tests are set to spawn 3 workers and run in parallel. This is configured
in [pyproject.toml](../pyproject.toml) under the pytest options. The project
installs [pytest-xdist](https://pytest-xdist.readthedocs.io/en/stable/index.html) to enable this.
