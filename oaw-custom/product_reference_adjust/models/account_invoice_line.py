# Copyright 2019 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    prod_ref = fields.Char(
        related="product_id.product_tmpl_id.name",
        string="Product Reference",
        store=True,
    )
    prod_code = fields.Char(
        related="product_id.product_tmpl_id.default_code", string="Code", store=True
    )
