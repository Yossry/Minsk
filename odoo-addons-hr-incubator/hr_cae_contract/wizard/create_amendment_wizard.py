# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class CreateAmendmentWizard(models.TransientModel):
    _name = "hr.contract.amendment.wizard"
    _description = "Create Contract Amendment"

    contract_id = fields.Many2one(
        comodel_name="hr.contract", string="Amendment of"
    )
    type_id = fields.Many2one(
        comodel_name="hr.contract.type",
        string="Contract Type",
        domain="[('echelon', '=', 'amendment')]",
        required=True,
        default="",
        copy=False,
    )

    @api.model
    def default_get(self, field_names):
        defaults = super().default_get(field_names)
        contract_id = self.env.context["active_id"]
        defaults["contract_id"] = contract_id
        return defaults

    @api.multi
    def create_amendment(self):
        self.ensure_one()
        return self.contract_id.create_amendment(self.type_id)
