# Copyright 2019 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_mto = fields.Boolean(string="Make to Order")
    # For Search
    lot_id = fields.Many2one(related="order_line.lot_id", string="Case No.")

    @api.multi
    def action_confirm(self):
        for sale_order in self:
            for order_line in sale_order.order_line:
                if order_line.quant_id.reservation_id:
                    raise UserError(
                        _(
                            "There is an invalid quant (pending "
                            "move exists for the quant)."
                        )
                    )
                order_line.quant_id.sudo().update({"sale_order_id": sale_order.id})
        return super(SaleOrder, self).action_confirm()

    @api.constrains("order_line")
    def _validate_order_line_lot_id(self):
        for rec in self:
            lot_ids = []
            for order_line in rec.order_line:
                if order_line.lot_id:
                    lot_ids.append(order_line.lot_id)
            if len(lot_ids) != len(set(lot_ids)):
                raise ValidationError(
                    _("You cannot select the same quant " "more than once in an SO.")
                )
