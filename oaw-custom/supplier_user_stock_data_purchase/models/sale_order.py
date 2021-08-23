# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    stock_data_purchase_history_id = fields.One2many(
        "stock.data.purchase.history",
        "sale_order_id",
        string="Stock Data Purchase Record",
    )
