# Copyright 2019 chrono123 & Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("partner_offer_checked")
    def _onchange_partner_offer_checked(self):
        if self.partner_offer_checked:
            self.qty_down = False
            self.qty_up = False
            self.costprice_up = False
            self.costprice_down = False
            self.note_updated = False

    @api.multi
    def _check_offer_checked(self):
        if all([product.product_tmpl_id.partner_offer_checked for product in self]):
            self.mapped("product_tmpl_id").update({"partner_offer_checked": False})
        else:
            self.filtered(
                lambda product: not product.product_tmpl_id.partner_offer_checked
            ).mapped("product_tmpl_id").update({"partner_offer_checked": True})
