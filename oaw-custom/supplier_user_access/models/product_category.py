# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    supplier_access = fields.Boolean(
        "Available for Supplier", default=False, store=True
    )

    @api.multi
    def name_get(self):
        context = self._context or {}
        if context.get("supplier_access_context", False):
            res = []
            for cat in self:
                res.append((cat.id, cat.name))
            return res
        else:
            return super(ProductCategory, self).name_get()
