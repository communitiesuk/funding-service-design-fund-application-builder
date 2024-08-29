# Prototype Fund Application Builder (FAB)
Flask app, with database, for building a fund and applications.

# Run
## Dev Containers
This repo contains a devcontainer spec for VS code at [.devcontainer](.devcontainer/python-container/devcontainer.json). This uses docker-compose to start up a container to develop the app, and also a companion postgres instance. The default connection URLs used for tests and at runtime are set to pickup the DB from that docker-compose instance so you don't need to set anything up manually.

## Local development
If developing locally, you will need a postgres instance running and to set the following environment variables:
 - `DATABASE_URL` to a suitable connection string. The default used is
 `postgresql://postgres:password@fab-db:5432/fund_builder`.   # pragma: allowlist secret
 - `DATABASE_URL_UNIT_TEST` default
 `postgresql://postgres:password@fab-db:5432/fund_builder_unit_test`  # pragma: allowlist secret

## General
Run the app with `flask run` (include `--debug` for auto reloading on file changes)

## Helper Tasks
Contained in [db_tasks.py](./tasks/db_tasks.py)

## Configuration Export Tasks
Contained in [export_tasks.py](./tasks/export_tasks.py)

The configuration output is generated by the [config_generator](./app/export_config/README.md) module. This module contains functions to generate fund and round configuration, form JSONs, and HTML representations for a given funding round.

## Database
### Schema
The database schema is defined in [app/db/models.py](./app/db/models.py) and is managed by Alembic. The migrations are stored in [app/db/migrations/versions](./app/db/migrations/versions/)

### Entity Relationship Diagram
See [Here](./app/db/database_ERD_9-8-24.png)

### Recreate Local DBs
For both `DATABASE_URL` and `DATABASE_URL_UNIT_TEST`, drops the database if it exists and then recreates it.

### Init migrations
Deletes the [versions](./app/db/migrations/versions/) directory and runs `migrate()` to generate a new intial migration version for the SQLAlchemy models.

### Create Test Data
Inserts a set of seed data comprising one Fund, 2 rounds and the applicaiton/assessment config for one of those rounds. The data created is defined in [test_data.py](./tasks/test_data.py)

## With Form Runner for Form Previews
In order to use the 'Preview Form' function, FAB needs to connect to a running instance of form runner. For prototyping, no session is created in the form runner, so it needs to be started without expecting the JWT information.

Below is a docker-compose file that will start both the FAB app, and the form runner, with the appropriate connection information. FAB will start on http://localhost:8080 and connect to the form runner defined in docker compose. If you want to do this, create the following directory structure and put this file in docker-compose.yml under DC.


```
    workspace
     | - dc
     |      - docker-compose.yml
     | - digital-form-builder
     | - funding-service-design-fund-application-builder
```

```
services:
  fab:
    hostname: fab
    build:
      context: ../funding-service-design-fund-application-builder
      dockerfile: Dockerfile
    command: ["sh", "-c", "python -m flask db upgrade && inv create-test-data && python -m flask run --host 0.0.0.0 --port 8080"]
    ports:
      - 8080:8080
    environment:
      - FORM_RUNNER_INTERNAL_HOST=http://form-runner:3009
      - FORM_RUNNER_EXTERNAL_HOST=http://localhost:3009
      - DATABASE_URL=postgresql://postgres:password@fab-db:5432/fund_builder   # pragma: allowlist secret
    depends_on: [fab-db]

  fab-db:
    image: postgres
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fund_builder

  form-runner:
    build:
      context: ../digital-form-builder
      dockerfile: ./fsd_config/Dockerfile
    command: yarn runner startdebug
    links:
      - fab:fab
    ports:
      - 3009:3009
      - 9228:9228
    environment:
      - LOG_LEVEL=debug
      - 'NODE_CONFIG={"safelist": ["fab"]}'
      - CONTACT_US_URL=http://localhost:3008/contact_us
      - FEEDBACK_LINK=http://localhost:3008/feedback
      - COOKIE_POLICY_URL=http://localhost:3008/cookie_policy
      - ACCESSIBILITY_STATEMENT_URL=http://localhost:3008/accessibility_statement
      - SERVICE_START_PAGE=http://localhost:3008/account
      - MULTIFUND_URL=http://localhost:3008/account
      - LOGOUT_URL=http://localhost:3004/sessions/sign-out
      - PRIVACY_POLICY_URL=http://localhost:3008/privacy
      - ELIGIBILITY_RESULT_URL=http://localhost:3008/eligibility-result
      - PREVIEW_MODE=true
      - NODE_ENV=development
```
