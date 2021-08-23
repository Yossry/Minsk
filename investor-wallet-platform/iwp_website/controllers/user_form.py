# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""User Form"""

from datetime import date

from odoo.addons.base_iban.models import res_partner_bank
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.translate import _

from .form import Choice, Field, Form, FormValidationError


class AddressForm(Form):
    """Form to get an address."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "street"] = Field(
            label=_("Address"),
            required=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "zip_code"] = Field(
            label=_("Zip / Postal Code"),
            required=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "city"] = Field(
            label=_("City"),
            required=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "country"] = Field(
            label=_("Country"),
            required=True,
            template="iwp_website.selection_field",
            choices=self._choices_country,
        )

    def _choices_country(self):
        countries = request.env["res.country"].sudo().search([])
        choices = []
        for country in countries:
            choices.append(
                Choice(
                    value=str(country.id), display=country.name, obj=country
                )
            )
        return choices


class BankAccountForm(Form):
    """Form to get an bank account number."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "bank_account"] = Field(
            label=_("Bank Account Number"),
            required=True,
            validators=[self._validate_bank_account],
            template="iwp_website.input_field",
            input_type="text",
        )

    def _validate_bank_account(self, value):
        try:
            res_partner_bank.validate_iban(value)
        except ValidationError:
            raise FormValidationError(_("Please give a correct IBAN number."))


class LanguageForm(Form):
    """Form to get the language of a user."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "lang"] = Field(
            label=_("Language"),
            required=True,
            template="iwp_website.selection_field",
            choices=self._choices_lang,
        )

    def _choices_lang(self):
        langs = request.env["res.lang"].sudo().search([])
        choices = []
        for lang in langs:
            choices.append(
                Choice(value=str(lang.code), display=lang.name, obj=lang)
            )
        return choices


class PersonForm(Form):
    """Form to edit information about an person."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "firstname"] = Field(
            label=_("Firstname"),
            required=True,
            att={"autofocus": "autofocus"},
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "lastname"] = Field(
            label=_("Lastname"),
            required=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "gender"] = Field(
            label=_("Gender"),
            required=True,
            template="iwp_website.selection_field",
            choices=self._choices_gender,
        )
        self.fields[prefix + "birthdate"] = Field(
            label=_("Birthdate"),
            required=True,
            att={"max": date.today().isoformat()},
            validators=[self._validate_birthdate],
            template="iwp_website.input_field",
            input_type="date",
        )
        self.fields[prefix + "phone"] = Field(
            label=_("Phone"),
            required=True,
            template="iwp_website.input_field",
            input_type="tel",
        )

    def _validate_birthdate(self, value, field):
        """Validate birthdate. Raise Error if validation doesn't succeed."""
        maximum = field.att.get("max")
        if maximum and value > field.to_python(maximum):
            raise FormValidationError(_("Bithdate must be in the past."))

    def _choices_gender(self):
        sub_req_mgr = request.env["subscription.request"]
        gender_field = sub_req_mgr.sudo().fields_get(["gender"])["gender"]
        choices = []
        for gender in gender_field["selection"]:
            choices.append(
                Choice(value=str(gender[0]), display=gender[1], obj=gender)
            )
        return choices


class CompanyForm(Form):
    """Form to edit information about an company."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "name"] = Field(
            label=_("Company Name"),
            required=True,
            att={"autofocus": "autofocus"},
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "phone"] = Field(
            label=_("Phone"),
            required=True,
            template="iwp_website.input_field",
            input_type="tel",
        )


class InvestorPersonForm(
    PersonForm, BankAccountForm, LanguageForm, AddressForm
):
    """Form to edit informations about a investor."""

    def __init__(self, add_fields=True, **kwargs):
        super().__init__(**kwargs)
        if add_fields:
            self.add_fields()

    def add_fields(self):
        PersonForm.add_fields(self)
        BankAccountForm.add_fields(self)
        LanguageForm.add_fields(self)
        AddressForm.add_fields(self)


class InvestorCompanyForm(
    CompanyForm, BankAccountForm, LanguageForm, AddressForm, PersonForm
):
    """Form to edit informations about a company investor."""

    def __init__(self, add_fields=True, **kwargs):
        super().__init__(**kwargs)
        if add_fields:
            self.add_fields()

    def add_fields(self):
        CompanyForm.add_fields(self)
        BankAccountForm.add_fields(self)
        LanguageForm.add_fields(self)
        AddressForm.add_fields(self)
        PersonForm.add_fields(self, prefix="rep_")
        AddressForm.add_fields(self, prefix="rep_")
