# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def unlink(self):
        quant_ids = self.env["stock.quant"].browse()
        for order_line in self:
            if order_line.quant_id:
                quant_ids += order_line.quant_id
        res = super(SaleOrderLine, self).unlink()
        if quant_ids:
            quant_ids._update_prod_tmpl_reserved_qty()
        return res
