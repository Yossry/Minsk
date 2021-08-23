# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    sale_order_id = fields.Many2one(
        "sale.order", string="Related Sale Order", readonly=True
    )
