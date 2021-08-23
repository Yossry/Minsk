# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def write(self, vals):
        if "zip" in vals:
            self.env["value.log"].create(
                {
                    "model": "res.partner",
                    "field": "zip",
                    "record_id": self.id,
                    "previous_value": str(self.zip),
                    "new_value": str(vals.get("zip")),
                }
            )
        return super(ResPartner, self).write(vals)
