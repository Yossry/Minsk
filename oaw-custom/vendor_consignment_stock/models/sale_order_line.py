# Copyright 2014 Camptocamp - Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be
        created from a stock rule comming from a sale order line. This method
        could be override in order to add other custom key that could be used
        in move/po creation.
        """
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        if (
            self.stock_owner_id
            and self.stock_owner_id != self.order_id.partner_id
            and self.stock_owner_id != self.env.user.company_id.partner_id
        ):
            routes = (
                self.route_id
                | self.env.ref("stock.route_warehouse0_mto")
                | self.env.ref("vendor_consignment_stock.route_warehouse0_buy_vci")
            )
            values["route_ids"] = routes
        return values
