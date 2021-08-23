# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    purchase_order_id = fields.Many2one(
        "purchase.order", string="Purchase Order", readonly=True, copy=False
    )

    @api.multi
    def action_view_purchase_open(self):
        action = self.env.ref("purchase.purchase_order_action_generic").read()[0]
        action["res_id"] = self.purchase_order_id.id
        return action
