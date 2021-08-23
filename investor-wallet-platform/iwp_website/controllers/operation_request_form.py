# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Operation Request Form"""

from datetime import date

from odoo.http import request
from odoo.tools.translate import _

from .form import Choice, Field, Form, FormValidationError
from .tools import monetary_to_text


class OperationRequestForm(Form):
    """Form to create a new Operation Request"""

    def __init__(self, **kw):
        super().__init__(**kw)
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

    def clean(self):
        """Check that user does not sell to much shares."""
        cleaned_data = super().clean()
        if "share_type" not in cleaned_data:
            return cleaned_data
        if "quantity" not in cleaned_data:
            return cleaned_data
        user = self.context.get("user")
        share_type = (
            request.env["product.template"]
            .sudo()
            .browse(int(cleaned_data["share_type"]))
        )
        # Pending operation for this share type
        operation_reqs = request.env["operation.request"].sudo().search(
            [
                ("share_product_id", "=", share_type.product_variant_id.id),
                ("partner_id", "=", user.commercial_partner_id.id),
                ("state", "in", ["draft", "wainting", "approved"]),
                ("operation_type", "!=", "subscription"),
            ]
        )
        amount = share_type.list_price * cleaned_data["quantity"]
        owned_amount = user.commercial_partner_id.owned_amount(share_type)
        min_amount = share_type.minimum_amount
        selled_amount = sum(r.subscription_amount for r in operation_reqs)
        future_amount = owned_amount - selled_amount - amount
        if future_amount < 0 or 0 < future_amount < min_amount:
            raise FormValidationError(
                _(
                    "You cannot sell so much shares. You must sell all "
                    "your share or keep at least %d." % min_amount
                )
            )
        return cleaned_data

    def _validate_quantity(self, value, field):
        minimum = field.att.get("min")
        if minimum and value < minimum:
            raise FormValidationError("Minimun %d." % minimum)

    def _choices_share_type(self):
        user = self.context.get("user")
        struct = self.context.get("struct")
        share_types = request.env["product.template"].sudo()
        for shareline in user.commercial_partner_id.share_ids:
            if (
                shareline.share_product_id.structure == struct
                and shareline.creation_mode != "manual"
            ):
                share_types |= shareline.share_product_id.product_tmpl_id
        choices = []
        if struct:
            for st in share_types:
                choices.append(
                    Choice(
                        value=st.id,
                        display="%s - %s"
                        % (st.name, monetary_to_text(st.list_price)),
                        att={
                            "data-price": st.list_price,
                            "data-owned_amount": (
                                user.commercial_partner_id.owned_amount(st)
                                # TODO: remove pending operation request
                            ),
                            "data-min_amount": st.minimum_amount,
                        },
                        obj=st,
                    )
                )
        return choices
