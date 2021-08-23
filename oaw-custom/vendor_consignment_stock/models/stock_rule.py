# Copyright 2014 Camptocamp - Leonardo Pistone
# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    action = fields.Selection(selection_add=[("buy_vci", _("Buy VCI"))])

    @api.multi
    def _prepare_purchase_order(
        self, product_id, product_qty, product_uom, origin, values, partner
    ):
        if self.action == "buy_vci":
            if values.get("partner_id", False):
                partner = self.env["res.partner"].browse(values["partner_id"])
        values = super(StockRule, self)._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, partner
        )
        if self.action == "buy_vci":
            values.update({"is_vci": True})
        return values

    @api.multi
    def _run_buy_vci(
        self, product_id, product_qty, product_uom, location_id, name, origin, values
    ):
        if self.action == "buy_vci":
            if values.get("move_dest_ids", False):
                restrict_partner_ids = values["move_dest_ids"].mapped(
                    "restrict_partner_id"
                )
                if restrict_partner_ids:
                    partner = restrict_partner_ids[0]
                    values.update({"partner_id": partner.id})
        return super(StockRule, self)._run_buy(
            product_id, product_qty, product_uom, location_id, name, origin, values
        )
