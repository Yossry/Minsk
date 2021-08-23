# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EventRegistration(models.Model):
    _inherit = "event.registration"

    employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee", required=False
    )
    promotion_id = fields.Many2one(
        comodel_name="hr.promotion",
        string="Promotion",
        related="employee_id.promotion_id",
    )

    @api.onchange("employee_id")
    def onchange_employee_id(self):
        self.name = self.employee_id.name
        self.phone = self.employee_id.work_phone
        self.email = self.employee_id.work_email


class Event(models.Model):
    _inherit = "event.event"

    promotion_id = fields.Many2one(
        comodel_name="hr.promotion", string="Promotion", required=False
    )

    @api.multi
    def button_register_promotion(self):
        self.ensure_one()
        if not self.promotion_id:
            raise ValidationError(_("Enter a promotion first."))
        for employee in self.promotion_id.employee_ids:
            self.env["event.registration"].create(
                {
                    "event_id": self.id,
                    "name": employee.name,
                    "email": employee.work_email,
                    "phone": employee.work_phone,
                    "employee_id": employee.id,
                }
            )
