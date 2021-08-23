# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Subscription Request Form"""

from datetime import date

from odoo.http import request
from odoo.tools.translate import _

from .form import Choice, Field, Form, FormValidationError
from .tools import monetary_to_text


class LoanIssueLineForm(Form):
    """Form to create new Loan Issue Line for a user"""

    def __init__(self, **kw):
        super().__init__(**kw)
        context = kw["context"]
        self.fields["loan_issue"] = Field(
            label=_("Loan Issue"),
            required=True,
            template="iwp_website.selection_field",
            choices=self._choices_loan_issue,
        )
        self.fields["quantity"] = Field(
            label=_("Quantity"),
            required=True,
            att={"min": 1},
            validators=[self._validate_quantity],
            template="iwp_website.input_field",
            input_type="number",
        )
        self.fields["total_amount"] = Field(
            label=_("Total Amount"),
            readonly=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields["data_policy_approval"] = Field(
            label=_("Data Policy"),
            content=context["struct"].data_policy_approval_text,
            required=True,
            template="iwp_website.checkbox_field",
        )
        self.fields["internal_rules_approval"] = Field(
            label=_("Internal Rules"),
            content=context["struct"].internal_rules_approval_text,
            required=True,
            template="iwp_website.checkbox_field",
        )
        self.fields["financial_risk_approval"] = Field(
            label=_("Financial Risks"),
            content=context["struct"].financial_risk_approval_text,
            required=True,
            template="iwp_website.checkbox_field",
        )

    def clean(self):
        """Check that user does not buy to much shares."""
        cleaned_data = super().clean()
        if "loan_issue" not in cleaned_data:
            return cleaned_data
        if "quantity" not in cleaned_data:
            return cleaned_data
        user = self.context.get("user")
        loan_issue = (
            request.env["loan.issue"]
            .sudo()
            .browse(int(cleaned_data["loan_issue"]))
        )
        amount = loan_issue.face_value * cleaned_data["quantity"]
        max_amount = loan_issue.get_max_amount(user.commercial_partner_id)
        if max_amount == 0:
            raise FormValidationError(
                _(
                    "You have reached the maximum amount that can be taken "
                    "for this structure."
                )
            )
        if 0 < max_amount < amount:
            raise FormValidationError(
                _(
                    "You cannot request so much loans. The maximum amount"
                    " is %d."
                    % max_amount
                )
            )
        min_amount = loan_issue.get_min_amount(user.commercial_partner_id)
        if amount < min_amount:
            raise FormValidationError(
                _(
                    "You have to request more loans. Minimum amount is %d."
                    % min_amount
                )
            )
        return cleaned_data

    def _validate_quantity(self, value):
        if value <= 0:
            raise FormValidationError("Quantity can not be nul or negative.")

    def _choices_loan_issue(self):
        user = self.context.get("user")
        struct = self.context.get("struct")
        loan_issues = (
            request.env["loan.issue"]
            .sudo()
            .get_web_issues(user.commercial_partner_id.is_company)
            .filtered(lambda r: r.structure == struct)
        )
        choices = []
        if struct:
            for issue in loan_issues:
                choices.append(
                    Choice(
                        value=issue.id,
                        display="%s - %s"
                        % (issue.name, monetary_to_text(issue.face_value)),
                        att={
                            "data-face_value": issue.face_value,
                            "data-max_amount": issue.get_max_amount(
                                user.commercial_partner_id
                            ),
                            "data-min_amount": issue.get_min_amount(
                                user.commercial_partner_id
                            ),
                        },
                        obj=issue,
                    )
                )
        return choices
