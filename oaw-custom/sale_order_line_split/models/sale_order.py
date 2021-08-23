# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    need_split_line = fields.Boolean(
        compute="_check_need_split_line", store=True, default=False
    )

    @api.multi
    def action_split_line(self):
        for order in self:
            for order_line in order.order_line:
                if (
                    order_line.product_uom_qty > 1.0
                    and order_line.product_id.tracking in ("serial", "lot")
                ):
                    for _qty in range(1, int(order_line.product_uom_qty)):
                        order_line.copy(
                            default={"product_uom_qty": 1.0, "order_id": order.id}
                        )
                    order_line.product_uom_qty = 1.0
        order._update_order_line_sequence()
        order._check_need_split_line()

    @api.multi
    @api.depends("order_line")
    def _check_need_split_line(self):
        for order in self:
            order.need_split_line = False
            for order_line in order.order_line:
                if (
                    order_line.product_uom_qty > 1.0
                    and order_line.product_id.tracking in ("serial", "lot")
                ):
                    order.need_split_line = True
