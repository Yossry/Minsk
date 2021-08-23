# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    quant_owner_related_user_id = fields.Many2one(
        "res.users", compute="get_quant_owner_related_user_id", store=True
    )
    supplier_pick_partner = fields.Char(
        string="Pick Partner", compute="get_supplier_pick_partner"
    )

    @api.multi
    @api.depends("quant_id", "quant_owner_id.user_ids")
    def get_quant_owner_related_user_id(self):
        for move in self:
            quant_owner_id = False
            if move.quant_id:
                quant_owner_id = move.quant_id[0].owner_id
            if quant_owner_id and quant_owner_id.sudo().user_ids:
                move.quant_owner_related_user_id = quant_owner_id.sudo().user_ids[0].id

    @api.multi
    def get_supplier_pick_partner(self):
        for move in self:
            if (
                move.picking_partner_id.sudo().related_partner
                and move.picking_partner_id.sudo().related_partner
                == self.env.user.partner_id
            ):
                move.supplier_pick_partner = move.picking_partner_id.sudo().name
            else:
                move.supplier_pick_partner = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("supplier_user_access.default_supplier_pick_partner")
                )
