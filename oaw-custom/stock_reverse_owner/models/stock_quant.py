# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    repair = fields.Boolean(
        string="Repair", related="location_id.return_location", store=True
    )
