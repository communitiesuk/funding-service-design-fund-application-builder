import datetime

import pytest
from bs4 import BeautifulSoup
from werkzeug.datastructures import MultiDict
from wtforms.fields.datetime import DateTimeField
from wtforms.form import Form

from govuk_frontend_ext.fields import GovDatetimeInput


class TestDatetimeField:
    @pytest.mark.parametrize(
        "data, expected_values",
        (
            (None, [None] * 5),
            (datetime.datetime(2000, 1, 2, 10, 30, 00), ["02", "01", "2000", "10", "30"]),
        ),
    )
    def test_fields_render(self, app, data, expected_values):
        class _Form(Form):
            field = DateTimeField(None, format="%Y %m %d %H %M", widget=GovDatetimeInput())

        form = _Form(data={"field": data})

        with app.app_context():
            html = form.field()

        soup = BeautifulSoup(html, "html.parser")
        assert len(soup.find_all("input")) == 5

        assert [el.get("id") for el in soup.find_all("input")] == [
            "field",
            "field-month",
            "field-year",
            "field-hour",
            "field-minute",
        ]

        assert [el.get("value") for el in soup.find_all("input")] == expected_values

    def test_fields_render_errors(self, app):
        class _Form(Form):
            field = DateTimeField(None, format="%Y %m %d %H %M", widget=GovDatetimeInput())

        expected_values = ["02", "01", "2000", "10", "30"]

        form = _Form()
        form.process(formdata=MultiDict([("field", val) for val in expected_values]))
        form.validate()
        assert form.errors == {"field": ["Not a valid datetime value."]}

        with app.app_context():
            html = form.field()

        soup = BeautifulSoup(html, "html.parser")
        assert len(soup.find_all(class_="govuk-error-message")) == 1
        assert soup.find(class_="govuk-error-message").text.strip() == "Error: Not a valid datetime value."
        assert len(soup.find_all(class_="govuk-input--error")) == 5
