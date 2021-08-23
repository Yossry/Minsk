# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    website_size_x = fields.Integer("Size X", default=1)
    website_size_y = fields.Integer("Size Y", default=1)
    website_style_ids = fields.Many2many("product.style", string="Styles")
    name = fields.Char(related="product_id.product_tmpl_id.name", store=True,)
    category_name = fields.Char(
        related="product_id.product_tmpl_id.category_name", store=True,
    )
    default_code = fields.Char(
        related="product_id.product_tmpl_id.default_code", store=True,
    )
    image = fields.Binary(related="product_id.product_tmpl_id.image",)
    special_offer = fields.Float(string="Special Offer")
    new_arrival = fields.Boolean(string="New Arrival")
    custom_image = fields.Binary(string="Custom Image")

    # Overwriting display_name's method for Supplier Access User
    @api.multi
    def name_get(self, *args, **kwargs):
        result = []
        for rec in self:
            result.append((rec.id, rec.product_id.sudo().name))
        return result
