# Copyright 2019 chrono123 & Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.picking"

    # For VCI receipt: Check if "Currency Amount Price Change' (purchase price) changes
    # with consecutive effect on filter
    @api.multi
    def write(self, vals):
        # Check if the stock.picking is being confirmed
        for picking in self:
            if "date_done" in vals and picking.picking_type_id.code == "incoming":
                for stock_move in picking.move_lines:
                    for stock_move_line in stock_move.move_line_ids:
                        if stock_move_line.owner_id.id != 1:
                            # Look through existing quants of given produdct_id
                            domain = [
                                ("product_id", "=", stock_move_line.product_id.id),
                                ("write_date", "<", stock_move_line.write_date),
                                ("currency_id", "=", stock_move_line.currency_id.id),
                            ]
                            last_stock_quant = self.env["stock.quant"].search(
                                domain, order="create_date DESC"
                            )
                            if last_stock_quant:
                                if (
                                    last_stock_quant[0].id
                                    != stock_move_line.quant_id.id
                                ):
                                    if (
                                        last_stock_quant[0].purchase_price_unit
                                        != stock_move_line.purchase_price_unit
                                    ):
                                        stock_move_line.product_id.product_tmpl_id.sudo().write(  # noqa
                                            {
                                                "currency_price_change_date": fields.Datetime.now(),  # noqa
                                                "partner_offer_checked": False,
                                            }
                                        )
        return super(StockMove, self).write(vals)
