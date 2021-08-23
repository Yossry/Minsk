# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    subtotal_hkd = fields.Float(
        string="Subtotal in HKD",
        digits=dp.get_precision("Product Price"),
        readonly=True,
    )

    @api.multi
    def _update_product_sale_info(self):
        for order_line in self:
            rate = 1.0
            if (
                order_line.order_id.date_order
                and order_line.order_id.currency_id
                != self.env.user.company_id.currency_id
            ):
                rate = self.env["res.currency"]._get_conversion_rate(
                    order_line.order_id.currency_id,
                    self.env.user.company_id.currency_id,
                    self.env["res.users"]._get_company(),
                    order_line.order_id.date_order,
                )
            order_line.subtotal_hkd = order_line.price_subtotal * rate
            order_line.product_id.product_tmpl_id.update(
                {
                    "total": order_line.product_id.product_tmpl_id.total
                    + order_line.subtotal_hkd,
                    "counts": order_line.product_id.product_tmpl_id.counts
                    + order_line.product_uom_qty,
                }
            )
