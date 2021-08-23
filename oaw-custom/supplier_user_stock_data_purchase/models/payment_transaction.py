# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    @api.multi
    def write(self, vals):
        if "state" in vals and vals["state"] == "done":
            self.mapped("sale_order_ids").mapped(
                "stock_data_purchase_history_id"
            ).sudo().update({"payment_confirm": True, "data_generation_pending": True})
        return super(PaymentTransaction, self).write(vals)
