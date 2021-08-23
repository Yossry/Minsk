# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.is_vci:
                order.group_id.sale_id.picking_ids.mapped("move_lines").filtered(
                    lambda l: l.state == "waiting"
                )._recompute_state()
        return res
