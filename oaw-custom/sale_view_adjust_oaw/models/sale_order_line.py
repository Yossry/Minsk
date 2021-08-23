# Copyright 2019 Quartile Limted
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    note_client_name = fields.Char(string="Note Client Name")
    note_client_price = fields.Char(string="Note Client Price")
    image_medium = fields.Binary(
        "Image", related="product_id.product_tmpl_id.image_medium", readonly=True
    )
    line_sequence = fields.Integer(string="Sequence", readonly=True)
