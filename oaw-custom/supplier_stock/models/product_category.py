# Copyright 2018 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.multi
    def name_get(self):
        context = self._context or {}
        if context.get("product_selection", False):
            res = []
            for cat in self:
                res.append((cat.id, cat.name))
            return res
        else:
            return super(ProductCategory, self).name_get()
