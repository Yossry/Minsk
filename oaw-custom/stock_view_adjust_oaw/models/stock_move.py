# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    image_medium = fields.Binary(
        "Image", related="product_id.product_tmpl_id.image_medium", readonly=True
    )
    line_sequence = fields.Integer(string="Sequence", readonly=True)
