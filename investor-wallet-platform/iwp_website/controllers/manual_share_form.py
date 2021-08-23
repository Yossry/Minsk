# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Manual Share Form"""

from collections import OrderedDict
from datetime import date

from odoo.http import request
from odoo.tools.translate import _

from .form import Choice, Field, Form, FormValidationError
from .tools import monetary_to_text


class ManualShareForm(Form):
    """Form to create new Manual Share for a user"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.fields = OrderedDict()
        self.fields["share_type"] = Field(
            label=_("Share Type"),
            required=True,
            template="iwp_website.selection_field",
            choices=self._choices_share_type,
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

    def _choices_share_type(self):
        user = self.context.get("user")
        struct = self.context.get("struct")
        if user.is_company:
            share_types = struct.share_type_ids.filtered(
                lambda r: r.display_on_website and r.by_company
            )
        else:
            share_types = struct.share_type_ids.filtered(
                lambda r: r.display_on_website and r.by_individual
            )
        choices = []
        if struct:
            for st in share_types:
                choices.append(
                    Choice(
                        value=str(st.id),
                        display="%s - %s"
                        % (st.name, monetary_to_text(st.list_price)),
                        att={"data-amount": st.list_price},
                        obj=st,
                    )
                )
        return choices
