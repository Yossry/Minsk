# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    _trigger_field = fields.Boolean(
        string="internal trigger field", compute="_compute_trigger", store=True
    )

    @api.multi
    def write(self, vals):
        if "address_home_id" in vals:
            if self.address_home_id:
                # fixme track zip changes
                old_home_address = self.address_home_id.zip
            else:
                old_home_address = False

            partner = self.env["res.partner"].browse(
                vals.get("address_home_id")
            )

            self.env["value.log"].create(
                {
                    "model": "hr.employee",
                    "field": "address_home_id.zip",
                    "record_id": self.id,
                    "previous_value": old_home_address,
                    "new_value": partner.zip,
                }
            )

        if "address_id" in vals:
            if self.address_id:
                old_address = self.address_id.zip
            else:
                old_address = False

            partner = self.env["res.partner"].browse(vals.get("address_id"))

            self.env["value.log"].create(
                {
                    "model": "hr.employee",
                    "field": "address_id.zip",
                    "record_id": self.id,
                    "previous_value": old_address,
                    "new_value": partner.zip,
                }
            )
        return super(Employee, self).write(vals)

    @api.depends("address_home_id.zip")
    def _compute_trigger(self):
        for employee in self:
            self.env["value.log"].create(
                {
                    "model": "hr.employee",
                    "field": "address_home_id.zip",
                    "record_id": employee.id,
                    "previous_value": "see value log for partner %s"
                    % employee.address_home_id.id,
                    "new_value": employee.address_home_id.zip,
                }
            )
            employee._trigger_field = False
