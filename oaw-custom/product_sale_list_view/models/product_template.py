# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    total = fields.Float(
        string="Total HKD", digits=dp.get_precision("Product Price"), readonly=True
    )
    average = fields.Float(
        string="Average Price",
        digits=dp.get_precision("Product Price"),
        compute="_compute_average",
    )
    counts = fields.Integer("Qty of all Sale Order Lines", readonly=True)

    @api.multi
    def _compute_average(self):
        for product in self:
            if product.counts:
                product.average = product.total / product.counts

    @api.multi
    def _update_sale_info(self):
        self.update({"total": 0, "counts": 0})
        self.env["sale.order.line"].search(
            [
                ("product_id", "in", self.mapped("product_variant_ids").ids),
                ("state", "in", ("sale", "done")),
            ]
        )._update_product_sale_info()

    @api.multi
    def action_open_order_line(self):
        view_id = self.env.ref("product_sale_list_view.sale_order_line_tree_view").id
        return {
            # for better record representation, set the name
            "name": self.default_code,
            "view_mode": "tree",
            "res_model": "sale.order.line",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "target": "current",
            "domain": [
                ("product_id", "in", self.product_variant_ids.ids),
                ("state", "in", ("sale", "done")),
            ],
        }
