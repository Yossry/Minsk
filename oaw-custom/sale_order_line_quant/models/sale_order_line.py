# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    quant_id = fields.Many2one("stock.quant", string="Stock Quant", copy=False)
    lot_id = fields.Many2one(related="quant_id.lot_id", string="Case No.", store=True)
    tracking = fields.Selection(
        related="product_id.tracking", string="Product Tracking"
    )
    stock_owner_id = fields.Many2one(related="quant_id.owner_id", string="Stock Owner")
    is_mto = fields.Boolean(related="order_id.is_mto", store=True, string="Is MTO?")
    quant_price_unit = fields.Float(related="lot_id.price_unit", string="Cost")

    @api.onchange("quant_id")
    def _onchange_quant_id(self):
        if self.quant_id:
            self.stock_owner_id = self.quant_id.owner_id
            if self.quant_id.purchase_price_unit > 0:
                self.purchase_price = self.env["res.currency"].compute(
                    self.quant_id.purchase_price_unit, self.quant_id.currency_id
                )
            else:
                self.purchase_price = (
                    self.quant_id.product_id.stock_value
                    / self.quant_id.product_id.qty_available
                )

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        values.update({"quant_id": self.quant_id.id, "lot_id": self.lot_id.id})
        return values

    @api.constrains("product_id", "quant_id", "state")
    def _validate_quant(self):
        for rec in self:
            if (
                rec.product_id.tracking in ("serial", "lot")
                and not rec.quant_id
                and rec.state == "sale"
            ):
                raise ValidationError(
                    _(
                        "You must select a quant "
                        "for products tracking with Serial Number"
                    )
                )

    @api.multi
    def write(self, vals):
        if "quant_id" in vals:
            for order_line in self:
                order_line.quant_id.sudo().update({"sale_order_id": False})
                if vals["quant_id"]:
                    self.env["stock.quant"].browse(vals["quant_id"]).sudo().update(
                        {"sale_order_id": order_line.order_id.id}
                    )
        return super(SaleOrderLine, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if "quant_id" in vals and vals["quant_id"]:
            res.quant_id.sudo().update({"sale_order_id": res.order_id.id})
        return res

    @api.multi
    def unlink(self):
        quant_ids = self.env["stock.quant"].browse()
        for order_line in self:
            if order_line.quant_id:
                quant_ids += order_line.quant_id
        res = super(SaleOrderLine, self).unlink()
        if quant_ids:
            quant_ids.sudo().update({"sale_order_id": False})
        return res

    @api.depends(
        "product_id",
        "quant_price_unit",
        "product_uom_qty",
        "price_unit",
        "price_subtotal",
    )
    def _product_margin(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            price = (
                currency.compute(
                    line.price_subtotal, self.env.user.company_id.currency_id
                )
                if currency != self.env.user.company_id.currency_id
                else line.price_subtotal
            )
            line.margin = self.env.user.company_id.currency_id.round(
                price - (line.quant_price_unit * line.product_uom_qty)
            )
