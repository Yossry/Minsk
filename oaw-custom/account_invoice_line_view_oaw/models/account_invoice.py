# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    payment_ref = fields.Char(
        string="Payment Reference", compute="_compute_payment_reference", store=True
    )

    @api.multi
    @api.depends("payment_ids")
    def _compute_payment_reference(self):
        for invoice in self:
            payment_ref = []
            for line in invoice.payment_ids:
                if line.payment_info and line.payment_info not in payment_ref:
                    payment_ref.append(line.payment_info)
            invoice.payment_ref = (
                ",".join(payment_ref) if len(payment_ref) > 0 else False
            )
