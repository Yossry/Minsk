# Copyright 2020 Quartile Limited, Timeware Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        if "state" in vals and vals["state"] == "sale":
            self.order_line._update_product_sale_info()
        return super(SaleOrder, self).write(vals)
