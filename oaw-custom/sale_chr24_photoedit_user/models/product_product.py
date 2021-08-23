# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # object action for chr24photo users to enter from tree view to their
    # custom form view
    @api.multi
    def action_view_product_open(self):
        view_id = self.env.ref("sale_chr24_photoedit_user.chrono24_view_form").id
        return {
            "name": "Product",
            "view_mode": "form",
            "view_type": "form",
            "res_model": "product.product",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": self.id,
            "target": "current",
        }
