# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    supplier_pick_partner = fields.Char("Default Pick Partner For Supplier")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        supplier_pick_partner = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("supplier_user_access.supplier_pick_partner", default=False)
        )
        res.update(supplier_pick_partner=supplier_pick_partner)
        return res

    @api.multi
    def set_values(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "supplier_user_access.supplier_pick_partner", self.supplier_pick_partner
        )
        super(ResConfigSettings, self).set_values()
