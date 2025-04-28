# Fund Application Builder (FAB)

## What is it?

Fund Application Builder (FAB) is a Flask-based web application that supports internal users in the Funding Service to configure new application rounds and assemble application tasklists. It was built to reduce the time taken to onboard new grants and open new application rounds for existing grants.

## How does it work?

This is the flow:

1. **Create a grant** - give details such as name and type (competitive / uncompeted)
2. **Create an application** - give details such as opening date, closing date and prospectus link
3. **Build the application** - assemble a list of forms that grant applicants will be required to fill out, grouped into sections
4. **Export the application** - download a ZIP file containing all of the configuration necessary for setting the new application round live

In order to build the application, you will need forms. You can upload forms (or "templates") to FAB via "Templates" -> "Upload template". These forms must be JSON files created by the [Form Designer](https://github.com/communitiesuk/digital-form-builder-adapter/tree/main/designer), which is a separate service. Form Designer handles granular forms concerns - individual pages (web forms), questions, data validation, branching logic, etc. - while FAB is used to assemble forms created by the Form Designer into a larger schema / tasklist, as well as configure all of the metadata around the application rounds and grants that these tasklists pertain to.

## Relationship to other services

**FAB is not currently directly connected to live, external user-facing services**. This is an important point to remember. Grants you create or applications you build in FAB will not be visible to external users, or have any effect on the world outside the Funding Service, until you export the configuration and manually load it into live services. This transfer process is currently a developer-led process, although work is ongoing to automate it.

That said, FAB does interact with other services...

In terms of direct interactions, FAB uses Form Runner (the complement to the Form Designer) for previewing forms, and Authenticator for... authentication. Authenticator uses Microsoft Entra ID. FAB is not a publicly available service - to access it, you must be a member of an invite-only user group within MHCLG's Azure AD tenant.

In terms of indirect interactions, Form Designer and the live services Apply and Assess are critical.

As mentioned under "How does it work?", Form Designer is used to produce the forms that are assembled to build applications in FAB. You create your form in the Designer, export it, and then upload it into FAB. FAB expects JSON in the very specific format that the Designer outputs, and in fact FAB's data schema is partially based around this format.

Regarding Apply and Assess - these are the user-facing applications, the things we ultimately care about. Apply supports local authorities and other organisations to apply for funding from a specific government grant. Assess is used by internal MHCLG assessors to validate and score grant applications submitted through Apply. The output of FAB is a set of configuration files that can be used to program Apply and Assess. The exact steps required to implement this vary and are constantly under review, but fundamentally it's about pushing all of that FAB data into data stores used by live services. This data push is a point-in-time thing - there is no ongoing connection between FAB and live services. They use different databases. It is well-known within the Funding Service that this is not an optimal, long-term solution.

## Local development

The recommended way to use FAB is to clone Funding Service's [Docker Runner repo](https://github.com/communitiesuk/funding-service-design-docker-runner) with `git clone git@github.com:communitiesuk/funding-service-design-docker-runner.git`, `cd` into the cloned directory `funding-service-design-docker-runner`, clone *this* repo into the `apps/` directory, and then run `docker compose up fab -d` from the Docker Runner repo root to leverage the existing Docker Compose configuration there, which handles requirements, environment variables and service dependencies (data persistence with PostgreSQL, authentication with Authenticator).

To run tests:

```bash
# Run unit and integration tests
uv run pytest

# Run end-to-end tests locally
uv run pytest --e2e

# Run E2E tests against Dev environment (assuming dev is the name of your AWS profile for the Dev environment)
uv run pytest --e2e --e2e-env dev --e2e-aws-vault-profile dev
```

The majority of tests require a connection to the local database, so please ensure you have the FAB database up and running before running tests. `docker compose up fab -d` handles database startup.

For further information on running E2E tests, please see [tests/e2e/README.MD](tests/e2e/README.MD).

To debug the application in VSCode, ensure FAB is running and that you have the `funding-service-design-docker-runner` directory open as your workspace, then go to the "Run and Debug" view in the sidebar and run the "Docker Runner: Fund Application Builder" configuration. This will allow you to insert breakpoints and intercept requests.
