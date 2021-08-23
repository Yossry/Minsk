# Copyright 2019-2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    usage = fields.Selection(
        related="location_id.usage",
        string="Type of Location",
        readonly=True,
        store=True,
    )
    actual_qty = fields.Float(
        compute="_compute_actual_qty",
        string="Actual Quantity",
        readonly=True,
        store=True,
    )
    currency_id = fields.Many2one(
        related="lot_id.currency_id",
        string="Purchase Currency",
        store=True,
        readonly=True,
    )
    purchase_price_unit = fields.Float(
        related="lot_id.purchase_price_unit",
        string="Purchase Currency Price",
        digits_compute=dp.get_precision("Product Price"),
        store=True,
        readonly=True,
    )
    original_owner_id = fields.Many2one(
        related="lot_id.original_owner_id",
        string="Original Owner",
        store=True,
        readonly=True,
    )
    exchange_rate = fields.Float(
        related="lot_id.exchange_rate",
        string="FX Rate",
        digits=(12, 6),
        store=True,
        readonly=True,
    )
    reservation_id = fields.Many2one(
        "stock.move", string="Reserved for Move", readonly=True
    )
    reservation_picking_id = fields.Many2one(
        related="reservation_id.picking_id",
        string="Reserved for Picking",
        readonly=True,
    )
    cost = fields.Float(related="lot_id.price_unit", string="Unit Cost", store=True)

    @api.multi
    @api.depends("reserved_quantity", "quantity")
    def _compute_actual_qty(self):
        for quant in self:
            quant.actual_qty = quant.quantity - quant.reserved_quantity

    @api.multi
    def name_get(self):
        res = []
        for quant in self:
            name = quant.product_id.code or ""
            if quant.lot_id:
                name = quant.lot_id.name
            name += ": {} {}".format(str(quant.quantity), quant.product_id.uom_id.name)
            res += [(quant.id, name)]
        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        # FIXME Improve the performance by passing the limit to the _search
        quant_ids = self.browse(self._search(args, access_rights_uid=name_get_uid))
        if name:
            lot_ids = self.env["stock.production.lot"]._search(
                [("name", operator, name)], limit=limit, access_rights_uid=name_get_uid
            )
            quant_ids = quant_ids.filtered(lambda q: q.lot_id.id in lot_ids)
        return quant_ids.name_get()
