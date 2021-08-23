# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    origin_invoice_line_id = fields.Many2one(
        "account.invoice.line", "Original Invoice Line", copy=True, readonly=True
    )
