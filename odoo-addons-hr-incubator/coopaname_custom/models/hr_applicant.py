# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super(Applicant, self).onchange_partner_id()
        self.name = self.partner_id.name
        self.partner_name = self.partner_id.name
        return res
