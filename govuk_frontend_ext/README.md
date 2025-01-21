## GOV.UK Frontend extension

This module provides additional components that extend what GOV.UK Frontend/GOV.UK Design System provides natively.

Specifically, it adds a 'date with time' form field component. GOV.UK Frontend only native supports a date field with day, month and year. We needed one that takes day, month, year, hour, minute.

As of creating this module, all of the code is heavily cribbed with minor modifications from [govuk-frontend-jinja](https://github.com/LandRegistry/govuk-frontend-jinja) and [govuk-frontend-wtf](https://github.com/LandRegistry/govuk-frontend-wtf).

As/when we update the version of govuk-frontend, govuk-frontend-jinja, and/or govuk-frontend-wtf, we will need to make sure that the components and macros inside this extensions folder are also updated.
