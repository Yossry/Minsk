# Copyright 2014-2015 Camptocamp SA - Yannick Vaucher, Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    stock_owner_id = fields.Many2one(comodel_name="res.partner", string="Stock Owner")
