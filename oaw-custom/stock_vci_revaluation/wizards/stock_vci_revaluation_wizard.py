# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockVciRevaluationWizard(models.TransientModel):
    _name = "stock.vci.revaluation.wizard"
    _description = "VCI Stock Revaluation Wizard"

    @api.multi
    def action_vci_stock_revaluation(self):
        self.ensure_one()
        if self.env.context.get("active_ids", False):
            quant_ids = self.env.context.get("active_ids")
        else:
            quant_ids = []
        self.env["stock.quant"].revaluate_vci_stock(quant_ids)
        return {"type": "ir.actions.act_window_close"}
