# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class HRContract(models.Model):
    _inherit = "hr.contract"

    @api.multi
    def write(self, vals):
        if "type_id" in vals:
            old_type = self.type_id.name if self.type_id else False
            new_type = (
                self.env["hr.contract.type"].browse(vals["type_id"]).name
            )

            self.env["value.log"].create(
                {
                    "model": "hr.contract",
                    "field": "type_id",
                    "record_id": self.id,
                    "previous_value": old_type,
                    "new_value": new_type,
                }
            )
        if "date_start" in vals:
            self.env["value.log"].create(
                {
                    "model": "hr.contract",
                    "field": "date_start",
                    "record_id": self.id,
                    "previous_value": self.date_start,
                    "new_value": vals.get("date_start"),
                }
            )
        if "date_end" in vals:
            self.env["value.log"].create(
                {
                    "model": "hr.contract",
                    "field": "date_end",
                    "record_id": self.id,
                    "previous_value": self.date_end,
                    "new_value": vals.get("date_end"),
                }
            )
        return super(HRContract, self).write(vals)
