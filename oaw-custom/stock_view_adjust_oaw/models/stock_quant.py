# Copyright 2019 Quartile Limted, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    client_order_ref = fields.Char(
        readonly=True, string="Remark Of SO", compute="_get_ref", store=True
    )
    quant_note = fields.Text("Note")
    image_medium = fields.Binary(
        "Image", related="product_id.product_tmpl_id.image_medium", readonly=True
    )

    @api.multi
    @api.depends("sale_order_id.client_order_ref")
    def _get_ref(self):
        for q in self:
            if q.sale_order_id:
                q.client_order_ref = q.sale_order_id.client_order_ref
