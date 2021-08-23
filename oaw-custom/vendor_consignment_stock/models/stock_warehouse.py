# Copyright 2014 Camptocamp - Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import Warning


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    buy_vci_to_resupply = fields.Boolean(
        "Purchase from VCI to resupply this warehouse",
        help="This warehouse can contain Vendor-Supplied-Inventory (VCI) that "
        "have to be bought before being sold.",
        default=True,
    )
    buy_vci_pull_id = fields.Many2one("stock.rule", "BUY VCI rule")

    @api.model
    def _get_buy_vci_pull_rule(self, warehouse):
        route_model = self.env["stock.location.route"]
        try:
            buy_vci_route = self.env.ref(
                "vendor_consignment_stock.route_warehouse0_buy_vci"
            )
        except Exception:
            buy_vci_route = route_model.search([("name", "like", _("Buy VCI"))])
        if not buy_vci_route:
            raise Warning(_("Can't find any generic Buy VCI route."))
        w_name = warehouse.name + " : " + _("Buy VCI")

        return {
            "name": w_name,
            "location_id": warehouse.int_type_id.default_location_dest_id.id,
            "route_id": buy_vci_route.id,
            "action": "buy_vci",
            "picking_type_id": warehouse.int_type_id.id,
            "warehouse_id": warehouse.id,
        }

    @api.model
    def create(self, vals):
        pull_model = self.env["stock.rule"]
        warehouse = super(StockWarehouse, self).create(vals)
        if warehouse.buy_vci_to_resupply:
            buy_vci_pull_vals = self._get_buy_vci_pull_rule(warehouse)
            buy_vci_pull = pull_model.create(buy_vci_pull_vals)
            warehouse.buy_vci_pull_id = buy_vci_pull.id
        return warehouse

    @api.multi
    def write(self, vals):
        pull_model = self.env["stock.rule"]
        if "buy_vci_to_resupply" in vals:
            if vals.get("buy_vci_to_resupply"):
                for warehouse in self:
                    if not warehouse.buy_vci_pull_id:
                        buy_vci_pull_vals = self._get_buy_vci_pull_rule(warehouse)
                        buy_vci_pull = pull_model.create(buy_vci_pull_vals)
                        vals["buy_vci_pull_id"] = buy_vci_pull.id
            else:
                for warehouse in self:
                    if warehouse.buy_vci_pull_id:
                        warehouse.buy_vci_pull_id.unlink()
        return super(StockWarehouse, self).write(vals)

    def _get_all_routes(self):
        all_routes = super(StockWarehouse, self)._get_all_routes()
        if self.buy_vci_to_resupply and self.buy_vci_pull_id.route_id:
            all_routes += self.buy_vci_pull_id.route_id
        return all_routes

    @api.model
    def _get_all_products_to_resupply(self, warehouse):
        product_ids = super(StockWarehouse, self)._get_all_products_to_resupply(
            warehouse
        )
        if warehouse.buy_vci_pull_id.route_id:
            for product in self.env["product.product"].browse(product_ids):
                for route in product.route_ids:
                    if route == warehouse.buy_vci_pull_id.route_id:
                        product_ids.remove(product.id)
                        break
        return product_ids

    def _update_name_and_code(self, new_name=False, new_code=False):
        res = super(StockWarehouse, self)._update_name_and_code(new_name, new_code)
        for warehouse in self:
            if warehouse.buy_vci_pull_id:
                warehouse.buy_vci_pull_id.write({"name": new_name})
        return res

    def _update_reception_delivery_resupply(self, reception_new, delivery_new):
        res = super(StockWarehouse, self)._update_reception_delivery_resupply(
            reception_new, delivery_new
        )  # v12
        for warehouse in self:
            if (
                warehouse.int_type_id.default_location_dest_id
                != warehouse.buy_vci_pull_id.location_id
            ):
                warehouse.buy_vci_pull_id.location_id = (
                    warehouse.int_type_id.default_location_dest_id
                )
        return res
