# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    updated_date = fields.Datetime(
        compute="update_updated_date", store=True, string="Updated Date"
    )

    @api.multi
    @api.depends(
        "list_price", "net_price", "qty_reserved", "qty_local_stock", "qty_overseas"
    )
    def update_updated_date(self):
        for product in self:
            product.updated_date = fields.Datetime.now()
