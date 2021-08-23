# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def update_updated_date(self):
        for p in self:
            p.product_tmpl_id.updated_date = fields.Datetime.now()
