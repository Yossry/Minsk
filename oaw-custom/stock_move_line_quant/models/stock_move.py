# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):
    _inherit = "stock.move"

    currency_id = fields.Many2one("res.currency", string="Purchase Currency")
    exchange_rate = fields.Float(string="FX Rate", digits=(12, 6))
    purchase_price_unit = fields.Float(
        string="Purchase Currency Price",
        digits_compute=dp.get_precision("Product Price"),
        store=True,
    )
    price_unit = fields.Float(
        string="Unit Price",
        digits=dp.get_precision("Product Price"),
        compute="_compute_price_unit",
        store=True,
    )
    quant_id = fields.Many2one("stock.quant", string="Stock Quant")
    lot_id = fields.Many2one(
        "stock.production.lot", related="quant_id.lot_id", string="Case No.", store=True
    )
    quant_owner_id = fields.Many2one(related="quant_id.owner_id", string="Quant Owner")
    product_uom_qty = fields.Float(default=1.0)

    @api.onchange("currency_id")
    def _onchange_currency_id(self):
        if self.currency_id:
            self.exchange_rate = self.currency_id.rate

    @api.multi
    @api.depends("purchase_price_unit", "currency_id", "exchange_rate")
    def _compute_price_unit(self):
        for move_line in self:
            if move_line.purchase_price_unit and move_line.exchange_rate:
                move_line.price_unit = (
                    move_line.purchase_price_unit / move_line.exchange_rate
                )

    def action_show_details(self):
        res = super(StockMove, self).action_show_details()
        res["context"].update(
            {"show_purchase_information": self.picking_type_id.code == "incoming"}
        )
        return res

    def _action_confirm(self, merge=True, merge_into=False):
        res = super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)
        for move in self:
            # Create stock.move.line for delivery if quant is specified
            if move.quant_id and not move.move_line_ids:
                values = {
                    "move_id": move.id,
                    "picking_id": move.picking_id.id,
                    "product_id": move.product_id.id,
                    "product_uom_id": move.product_uom.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                    "quant_id": move.quant_id.id,
                    "owner_id": move.quant_owner_id.id,
                    "lot_id": move.lot_id.id,
                    "product_uom_qty": 1.0,
                    "qty_done": 1.0,
                }
                self.env["stock.move.line"].create(values)
                move.quant_id.sudo().update({"reserved_quantity": 1})
        return res
