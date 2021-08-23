# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def revaluate_vci_stock(self, quant_ids=None):
        domain = [
            ("owner_id", "!=", self.env.user.company_id.partner_id.id),
            ("usage", "=", "internal"),
            ("purchase_price_unit", "!=", False),
        ]
        if quant_ids:
            domain.append(("id", "in", quant_ids))
        quants = self.search(domain)
        for quant in quants:
            rate = self.env["res.currency"]._get_conversion_rate(
                quant.currency_id,
                self.env.user.company_id.currency_id,
                self.env["res.users"]._get_company(),
                fields.Date.today(),
            )
            quant.lot_id.exchange_rate = rate
            quant.lot_id.price_unit = quant.purchase_price_unit * rate
        return True
