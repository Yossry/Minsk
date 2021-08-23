# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_assign(self):
        for picking in self:
            if picking.sale_id and self.env.context.get("button_assign"):
                picking.sale_id.confirm_vci_purhcase_order()
        return super(StockPicking, self).action_assign()
