# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    image_medium = fields.Binary(
        "Image", related="product_id.product_tmpl_id.image_medium", readonly=True
    )
    move_name = fields.Char(related="move_id.name", store=True)
    origin = fields.Char(related="move_id.origin", store=True)
    sale_order_id = fields.Many2one(related="move_id.sale_line_id.order_id")
    purchase_order_id = fields.Many2one(related="move_id.purchase_line_id.order_id")
    group_id = fields.Many2one(related="move_id.group_id")
    partner_id = fields.Many2one(related="move_id.partner_id")
    picking_partner_id = fields.Many2one(related="picking_id.partner_id")
    picking_type_id = fields.Many2one(related="move_id.picking_type_id")
    date_expected = fields.Datetime(related="move_id.date_expected")
