# Copyright 2020 Quartile Limted, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    supplier_sale_price = fields.Float(string="C123 Sale HKD")
    supplier_cost_price = fields.Float(string="C123 Cost HKD")
