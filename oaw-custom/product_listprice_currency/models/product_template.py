# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    retail_chf = fields.Float(
        string="Retail CHF", digits=dp.get_precision("Product Price")
    )
    retail_eur = fields.Float(
        string="Retail EUR", digits=dp.get_precision("Product Price")
    )
    retail_usd = fields.Float(
        string="Retail USD", digits=dp.get_precision("Product Price")
    )
    retail_rmb = fields.Float(
        string="Retail RMB", digits=dp.get_precision("Product Price")
    )
    price_last_update_date = fields.Datetime(
        readonly=True, string="Price Last Update Date"
    )
    price_last_update_user_id = fields.Many2one(
        "res.users", readonly=True, string="Price Last Update User"
    )

    @api.model
    def create(self, vals):
        vals.update(
            {
                "price_last_update_date": fields.Datetime.now(),
                "price_last_update_user_id": self.env.user.id,
            }
        )
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if (
            "list_price" in vals
            or "retail_chf" in vals
            or "retail_eur" in vals
            or "retail_usd" in vals
            or "retail_rmb" in vals
        ):
            vals.update(
                {
                    "price_last_update_date": fields.Datetime.now(),
                    "price_last_update_user_id": self.env.user.id,
                }
            )
        return super(ProductTemplate, self).write(vals)
