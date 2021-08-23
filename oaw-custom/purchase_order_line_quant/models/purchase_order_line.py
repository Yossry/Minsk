# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    quant_id = fields.Many2one("stock.quant", string="Stock Quant", copy=False)
    lot_id = fields.Many2one(related="quant_id.lot_id", string="Case No.", store=True)
