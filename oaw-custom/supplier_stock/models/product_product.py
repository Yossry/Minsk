# Copyright 2018 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def name_get(self):
        context = self._context or {}
        if context.get("product_selection", False):
            res = []
            for product in self:
                res.append((product.id, product.code))
            return res
        else:
            return super(ProductProduct, self).name_get()
