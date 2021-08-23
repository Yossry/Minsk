# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    stock_data_purchase_price = fields.Float(string="Stock Data Purchase Price")

    @api.multi
    def name_get(self):
        context = self._context or {}
        if context.get("purchase_stock_data", False):
            res = []
            for cat in self:
                res.append(
                    (
                        cat.id,
                        "{}: HKD {}".format(cat.name, cat.stock_data_purchase_price),
                    )
                )
            return res
        else:
            return super(ProductCategory, self).name_get()
