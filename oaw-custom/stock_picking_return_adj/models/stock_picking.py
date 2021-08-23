# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_returned = fields.Boolean(
        string="Is Returned",
        groups="stock.group_stock_manager",
        states={"done": [("readonly", False)]},
        compute="_compute_is_returned",
        store=True,
    )

    @api.multi
    @api.depends("move_lines.returned_move_ids")
    def _compute_is_returned(self):
        for picking in self:
            picking.is_returned = True if picking.returned_ids else False
