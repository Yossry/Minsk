# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SupplierStock(models.Model):
    _inherit = "supplier.stock"

    order_line_id = fields.Many2one(
        "sale.order.line", string="Order Reference", ondelete="cascade", readonly=True
    )
    order_id = fields.Many2one(
        related="order_line_id.order_id", string="Order Reference", readonly=True
    )
    pricelist_id = fields.Many2one(
        related="order_line_id.order_id.pricelist_id", string="Pricelist", readonly=True
    )
    order_partner_id = fields.Many2one(
        related="order_line_id.order_id.partner_id", string="Customer", readonly=True
    )
    order_price_unit = fields.Float(
        related="order_line_id.price_unit",
        string="Quotation Retail",
        store=True,
        readonly=False,
    )
    order_line_product_uom_qty = fields.Float(
        related="order_line_id.product_uom_qty", string="Qty"
    )
    order_line_margin = fields.Float(
        compute="_compute_order_line_margin", string="Margin"
    )

    @api.multi
    def _compute_order_line_margin(self):
        for supplier_stock in self:
            if supplier_stock.order_line_id:
                supplier_stock.order_line_margin = (
                    supplier_stock.order_line_id.price_subtotal
                    - supplier_stock.order_line_id.purchase_price
                )

    @api.multi
    def write(self, vals):
        res = super(SupplierStock, self).write(vals)
        if "order_price_unit" in vals:
            for supplier_stock in self:
                if supplier_stock.order_line_id:
                    supplier_stock.order_line_id.sudo().write(
                        {
                            "price_unit": vals["order_price_unit"]
                            if "order_price_unit" in vals
                            else supplier_stock.order_line_id.price_unit
                        }
                    )
        return res
