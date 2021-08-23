# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # For Search
    lot_id = fields.Many2one(related="invoice_line_ids.lot_id", string="Case No.")
