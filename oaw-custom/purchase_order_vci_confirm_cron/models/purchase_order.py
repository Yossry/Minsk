# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def confirm_purchase_order(self):
        orders = self.search([("is_vci", "=", True), ("state", "=", "draft")])
        for order in orders:
            order.button_confirm()
        return True
