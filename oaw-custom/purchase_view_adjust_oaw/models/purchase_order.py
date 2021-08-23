# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        for order in self:
            order._update_order_line_sequence()
        return res

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        for order in res:
            order._update_order_line_sequence()
        return res

    def _update_order_line_sequence(self):
        order_lines = sorted(self.order_line, key=lambda r: (r.line_sequence, r.id))
        sequence = 1
        for order_line in order_lines:
            order_line.line_sequence = sequence
            sequence += 1
