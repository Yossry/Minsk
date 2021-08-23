# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    partner_ref = fields.Char(string="Vendor Bill Reference")
    invoice_payment_status = fields.Selection(
        [("paid", "Paid"), ("unpaid", "Unpaid")],
        string="Payment Status",
        compute="_compute_payment_status",
        store=True,
    )

    @api.multi
    @api.depends("invoice_ids.state")
    def _compute_payment_status(self):
        for order in self:
            order.invoice_payment_status = "unpaid"
            if order.invoice_ids and all(
                [
                    invoice.state in ("paid", "cancel")
                    for invoice in order.mapped("invoice_ids")
                ]
            ):
                order.invoice_payment_status = "paid"
                if order.state != "done":
                    order.update({"state": "done"})
