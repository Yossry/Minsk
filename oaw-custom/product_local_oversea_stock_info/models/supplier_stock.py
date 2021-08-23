# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    @api.multi
    def _update_prod_tmpl_qty(self):
        for ss in self:
            ss.product_id._update_prod_tmpl_qty()

    @api.model
    def create(self, vals):
        res = super(SupplierStock, self).create(vals)
        product = self.env["product.product"].browse(vals.get("product_id", False))
        location = self.env["supplier.location"].browse(
            vals.get("partner_loc_id", False)
        )
        if product:
            if not location.hk_location:
                product.product_tmpl_id.sudo().write(
                    {
                        "qty_overseas": product.product_tmpl_id.qty_overseas
                        + int(vals.get("quantity", 0.0))
                    }
                )
            else:
                product.product_tmpl_id.sudo().write(
                    {
                        "qty_local_stock": product.product_tmpl_id.qty_available
                        + int(vals.get("quantity", 0.0))
                    }
                )
        if "partner_loc_id" in vals or "product_id" in vals or "quantity" in vals:
            product.product_tmpl_id.sudo()._compute_stock_location_info()
        return res

    @api.multi
    def write(self, vals):
        res = super(SupplierStock, self).write(vals)
        if "product_id" in vals or "quantity" in vals or "partner_loc_id" in vals:
            self._update_prod_tmpl_qty()
        if "partner_loc_id" in vals or "product_id" in vals or "quantity" in vals:
            for ss in self:
                ss.product_id.product_tmpl_id.sudo()._compute_stock_location_info()
        return res

    @api.multi
    def unlink(self):
        products = []
        for ss in self:
            products.append(ss.product_id.product_tmpl_id)
            if not ss.hk_location:
                qty_overseas = ss.product_id.product_tmpl_id.qty_overseas - int(
                    ss.quantity
                )
                ss.product_id.product_tmpl_id.sudo().write(
                    {"qty_overseas": qty_overseas}
                )
            else:
                qty_local_stock = ss.product_id.product_tmpl_id.qty_local_stock - int(
                    ss.quantity
                )
                ss.product_id.product_tmpl_id.sudo().write(
                    {"qty_local_stock": qty_local_stock}
                )
        res = super(SupplierStock, self).unlink()
        for product in products:
            product.sudo()._compute_stock_location_info()
        return res
