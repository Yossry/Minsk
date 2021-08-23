# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        for picking in self:
            picking._update_move_line_sequence()
        return res

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        for picking in res:
            picking._update_move_line_sequence()
        return res

    def _update_move_line_sequence(self):
        move_lines = sorted(self.move_lines, key=lambda r: (r.line_sequence, r.id))
        sequence = 1
        for move_line in move_lines:
            move_line.line_sequence = sequence
            sequence += 1
