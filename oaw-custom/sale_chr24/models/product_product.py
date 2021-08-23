# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def updated_chrono24_date_button(self):
        for product in self:
            product.product_tmpl_id.updated_date_chrono24 = fields.Datetime.now()
            product.product_tmpl_id.chrono24_updated = True
