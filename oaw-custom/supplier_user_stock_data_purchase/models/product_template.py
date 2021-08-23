# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    category_name = fields.Char(string="Brand", related="categ_id.name", store=True)
    update_partner_stock = fields.Boolean(
        string="Update Purchase Partner Stock Records"
    )

    @api.multi
    def write(self, vals):
        if (
            "qty_local_stock" in vals
            or "qty_overseas" in vals
            or "qty_reserved" in vals
        ):
            vals["update_partner_stock"] = True
        return super(ProductTemplate, self).write(vals)
