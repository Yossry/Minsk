# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Auth Sign up Form"""

from odoo import tools
from odoo.http import request
from odoo.tools.translate import _

from .form import Field, Form, FormValidationError
from .user_form import InvestorPersonForm, InvestorCompanyForm


class SignupForm(Form):
    """Form to signup with minimal information"""

    def add_fields(self):
        self.fields["login"] = Field(
            label=_("E-mail"),
            required=True,
            att={"autofocus": "autofocus", "autocapitalize": "off"},
            validators=[self._validate_login],
            template="iwp_website.input_field",
            input_type="email",
        )
        self.fields["confirm_login"] = Field(
            label=_("Confirm E-mail"),
            required=True,
            att={"autocapitalize": "off"},
            template="iwp_website.input_field",
            input_type="email",
        )
        self.fields["password"] = Field(
            label=_("Password"),
            required=True,
            validators=[self._validate_password],
            template="iwp_website.input_field",
            input_type="password",
        )
        self.fields["confirm_password"] = Field(
            label=_("Confirm Password"),
            required=True,
            template="iwp_website.input_field",
            input_type="password",
        )
        if (
            request.env["res.company"]
            ._company_default_get()
            .data_policy_approval_required
        ):
            self.fields["data_policy_approval"] = Field(
                label=_("Accept Data Policy"),
                required=True,
                template="iwp_website.checkbox_field",
            )

    def clean(self):
        """Validate that confirmation field are correctly filled in."""
        cleaned_data = super().clean()
        # Login and confirmation
        login = cleaned_data.get("login", self.data.get("login"))
        confirm_login = cleaned_data.get(
            "confirm_login", self.data.get("confirm_login")
        )
        if login != confirm_login:
            raise FormValidationError(
                _("The email and confirmation email must be the same.")
            )
        # Password and confirmation
        password = cleaned_data.get("password", self.data.get("password"))
        confirm_password = cleaned_data.get(
            "confirm_password", self.data.get("confirm_password")
        )
        if password != confirm_password:
            raise FormValidationError(
                _("The password and confirmation password does not match.")
            )
        return cleaned_data

    def _validate_login(self, value):
        """Validate login. Raise Error if validation doesn't succeed."""
        if not tools.single_email_re.match(value):
            raise FormValidationError(
                _("That does not seem to be an email address.")
            )

    def _validate_password(self, value):
        """Validate password. Raise Error if validation doesn't succeed."""
        if len(value) < 8:
            raise FormValidationError(
                _("Password must be at least 8 characters long.")
            )


class InvestorPersonSignupForm(SignupForm, InvestorPersonForm):
    """Form to register informations about a investor."""

    def __init__(self, **kwargs):
        super().__init__(add_fields=False, **kwargs)
        self.add_fields()

    def add_fields(self):
        SignupForm.add_fields(self)
        InvestorPersonForm.add_fields(self)


class InvestorCompanySignupForm(SignupForm, InvestorCompanyForm):
    """Form to register informations about a company investor."""

    def __init__(self, **kwargs):
        super().__init__(add_fields=False, **kwargs)
        self.add_fields()

    def add_fields(self):
        SignupForm.add_fields(self)
        InvestorCompanyForm.add_fields(self)
