# Copyright 2019-2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def name_get(self):
        context = {}
        context = dict(self.env.context)
        uid = context.get("uid")
        if context.get("supplier_access_context", False) or self.env[
            "res.users"
        ].browse(uid).has_group("supplier_user_access.group_supplier_fm"):
            res = []
            for product in self:
                res.append((product.id, product.name))
            return res
        else:
            return super(ProductProduct, self).name_get()
