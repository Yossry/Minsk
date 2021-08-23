# Copyright 2014-2015 Camptocamp SA - Yannick Vaucher, Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def create(self, values):
        move = super(StockMove, self).create(values)
        if move.sale_line_id and move.sale_line_id.stock_owner_id:
            move.restrict_partner_id = move.sale_line_id.stock_owner_id.id
        return move
