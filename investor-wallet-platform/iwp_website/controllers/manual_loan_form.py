# Copyright 2020 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Manual Loan Form"""

from collections import OrderedDict
from datetime import date

from odoo.http import request
from odoo.tools.translate import _

from .form import Choice, Field, Form, FormValidationError
from .tools import monetary_to_text


class ManualLoanForm(Form):
    """Form to create new Manual Share for a user"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.fields = OrderedDict()
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
        self.fields["date"] = Field(
            label=_("Date"),
            required=True,
            att={"max": date.today().isoformat()},
            validators=[self._validate_date],
            template="iwp_website.input_field",
            input_type="date",
        )

    def _validate_quantity(self, value):
        minimum = self.fields["quantity"].att.get("min")
        if minimum and value < minimum:
            raise FormValidationError("Minimun %d." % minimum)

    def _validate_date(self, value):
        maximum = self.fields["date"].att.get("max")
        if maximum and value > self.fields["date"].to_python(maximum):
            raise FormValidationError("Please enter date in the past.")

    def _choices_loan_issue(self):
        user = self.context.get("user")
        struct = self.context.get("struct")
        if user.is_company:
            loan_issues = struct.loan_issue_ids.filtered(
                lambda r: r.display_on_website and r.by_company
            )
        else:
            loan_issues = struct.loan_issue_ids.filtered(
                lambda r: r.display_on_website and r.by_individual
            )
        choices = []
        if struct:
            for issue in loan_issues:
                choices.append(
                    Choice(
                        value=issue.id,
                        display="%s - %s"
                        % (issue.name, monetary_to_text(issue.face_value)),
                        att={"data-face_value": issue.face_value},
                        obj=issue,
                    )
                )
        return choices
