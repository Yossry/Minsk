# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def unlink(self):
        quant_ids = self.env["stock.quant"].browse()
        for order in self:
            for line in order.order_line:
                if line.quant_id:
                    quant_ids += line.quant_id
        res = super(SaleOrder, self).unlink()
        if quant_ids:
            quant_ids._update_prod_tmpl_reserved_qty()
        return res
