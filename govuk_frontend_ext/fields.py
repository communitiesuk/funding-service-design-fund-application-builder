from govuk_frontend_wtf.gov_form_base import GovFormBase


class GovDatetimeInput(GovFormBase):
    """Renders five input fields representing Day, Month, Year, Hour, Minute.

    The original source of this input is from govuk-frontend-wtf:
    https://github.com/LandRegistry/govuk-frontend-wtf/blob/main/govuk_frontend_wtf/wtforms_widgets.py#L135

    And
    """

    template = "govuk_frontend_ext/datetime.html"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        return super().__call__(field, **kwargs)

    def map_gov_params(self, field, **kwargs):
        params = super().map_gov_params(field, **kwargs)
        day, month, year, hour, minute = [None] * 5
        if field.raw_data is not None:
            day, month, year, hour, minute = field.raw_data
        elif field.data:
            day, month, year, hour, minute = field.data.strftime("%d %m %Y %H %M").split(" ")

        params.setdefault(
            "fieldset",
            {
                "legend": {"text": field.label.text},
            },
        )
        params.setdefault(
            "items",
            [
                {
                    "label": "Day",
                    "id": "{}-day".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": day,
                },
                {
                    "label": "Month",
                    "id": "{}-month".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": month,
                },
                {
                    "label": "Year",
                    "id": "{}-year".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-4",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": year,
                },
                {
                    "label": "Hour",
                    "id": "{}-hour".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": hour,
                },
                {
                    "label": "Minute",
                    "id": "{}-minute".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": minute,
                },
            ],
        )
        return params
