# Copyright 2014 Camptocamp - Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_vci = fields.Boolean("Vendor Consignment Inventory")

    @api.multi
    def _create_picking(self):
        self.ensure_one()
        if self.is_vci:
            return False
        return super(PurchaseOrder, self)._create_picking()
