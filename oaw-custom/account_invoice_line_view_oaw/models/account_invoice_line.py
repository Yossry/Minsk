# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    user_id = fields.Many2one(
        "res.users", related="invoice_id.user_id", store=True, string="Salesperson",
    )
    number = fields.Char(related="invoice_id.number", store=True, string="Number")
    state = fields.Selection(related="invoice_id.state", store=True, string="Status")
    date_invoice = fields.Date(
        related="invoice_id.date_invoice", store=True, string="Invoice Date",
    )
    ref = fields.Char(
        related="invoice_id.partner_id.ref", store=True, string="Partner Ref",
    )
    reference = fields.Char(
        related="invoice_id.reference", string="Vendor Bill Reference"
    )
    date_due = fields.Date(related="invoice_id.date_due", string="Due Date")
    currency_id = fields.Many2one(related="invoice_id.currency_id", string="Currency")
    partner_ref = fields.Char("Supplier Reference", related="po_id.partner_ref",)
    rate = fields.Float(compute="_compute_base_amt", string="Rate", digits=(12, 6))
    base_amt = fields.Float(
        compute="_compute_base_amt",
        digits_compute=dp.get_precision("Account"),
        string="Base Amount",
    )
    so_id = fields.Many2one(
        "sale.order", compute="_compute_so_po_id", store=True, string="SO",
    )
    po_id = fields.Many2one(
        "purchase.order", compute="_compute_so_po_id", store=True, string="PO",
    )
    image_medium = fields.Binary(
        "Image", related="product_id.product_tmpl_id.image_medium",
    )
    reviewed = fields.Boolean("Reviewed")
    payment_reference = fields.Char(
        "Payment Reference", related="invoice_id.payment_ref", store=True
    )
    note = fields.Char("Note")

    @api.model
    def _get_org_vals(self, inv_ln):
        so_id, po_id = 0, 0
        SO = self.env["sale.order"]
        PO = self.env["purchase.order"]
        if inv_ln.invoice_id.origin:
            if inv_ln.invoice_id.type == "out_invoice" and SO.search(
                [("name", "=", inv_ln.invoice_id.origin)]
            ):
                so_id = SO.search([("name", "=", inv_ln.invoice_id.origin)])[0].id
            if inv_ln.invoice_id.type == "in_invoice" and PO.search(
                [("name", "=", inv_ln.invoice_id.origin)]
            ):
                po_id = PO.search([("name", "=", inv_ln.invoice_id.origin)])[0].id
        return so_id, po_id

    @api.multi
    @api.depends("invoice_id.state", "invoice_id.origin")
    def _compute_so_po_id(self):
        for inv_ln in self:
            inv_ln.so_id, inv_ln.po_id = self._get_org_vals(inv_ln)

    @api.multi
    def _compute_base_amt(self):
        for inv_ln in self:
            curr_amt = inv_ln.price_subtotal
            # set rate 1.0 if the transaction currency is the same as the base currency
            if inv_ln.currency_id == inv_ln.company_id.currency_id:
                rate = 1.0
            elif inv_ln.invoice_id.paid_date_currency_rate:
                rate = inv_ln.invoice_id.paid_date_currency_rate
            else:
                invoice_date = inv_ln.date_invoice or inv_ln.env.context.get(
                    "date", datetime.today().strftime("%Y-%m-%d")
                )
                rate = 1 / self.env["res.currency"]._get_conversion_rate(
                    inv_ln.currency_id,
                    inv_ln.company_id.currency_id,
                    inv_ln.company_id,
                    invoice_date,
                )
            inv_ln.rate = rate
            inv_ln.base_amt = curr_amt * (1 / rate)
