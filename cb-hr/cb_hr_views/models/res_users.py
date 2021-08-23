# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    notification_type = fields.Selection(default="inbox")

    def name_get(self):
        return super(
            ResUsers, self.with_context(not_display_company=True)
        ).name_get()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.partner_id.employee_ids:
            res.partner_id.employee_ids._compute_user()
        return res
