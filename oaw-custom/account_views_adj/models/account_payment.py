# Copyright 2019 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sale_order_ids = fields.Many2many(
        "sale.order", compute="_get_sale_order_ref", store=True, search="_search_by_so"
    )
    sale_order_id = fields.Char("Sale Order", related="sale_order_ids.display_name")
    payment_info = fields.Char("Payment Info")
    payment_reviewed = fields.Boolean("Checked")
    invoice_type = fields.Selection(related="invoice_ids.type")
    inverse_amount = fields.Monetary(string="Payment Amount")

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        if "amount" in rec and rec["amount"]:
            rec["inverse_amount"] = -rec["amount"]
        return rec

    @api.onchange("inverse_amount")
    def _onchange_payment_amount(self):
        if self.inverse_amount:
            self.amount = -self.inverse_amount

    def _search_by_so(self, operator, value):
        return [("sale_order_id", operator, value)]

    @api.multi
    def _get_sale_order_ref(self):
        for payment in self:
            payment.sale_order_ids = (
                payment.mapped("reconciled_invoice_ids")
                .mapped("invoice_line_ids")
                .mapped("sale_line_ids")
                .mapped("order_id")
            )

    @api.multi
    def open_payment(self):
        view_id = self.env.ref("account.view_account_payment_form").id
        return {
            "name": "Customer Payments",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "account.payment",
            "view_id": view_id,
            "res_id": self.id,
            "target": "current",
            "type": "ir.actions.act_window",
        }
