# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class WizardExtendHolidays(models.TransientModel):

    _name = "wizard.extend.holidays"
    _description = "wizard.extend.holidays"

    name = fields.Char()

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        readonly=True,
        related="holidays_id.employee_id",
    )

    date_from = fields.Date(
        readonly=True, related="holidays_id.request_date_from"
    )
    date_to = fields.Date()

    number_of_days = fields.Float(compute="_compute_number_of_days")

    holidays_id = fields.Many2one(comodel_name="hr.leave")

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        context = dict(self._context or {})
        active_id = context.get("active_id", False)
        if active_id:
            holiday = self.env["hr.leave"].browse(active_id)
            rec.update(
                {"holidays_id": holiday.id, "date_to": holiday.request_date_to}
            )
        return rec

    @api.depends("date_to")
    def _compute_number_of_days(self):
        time_delta = self.date_to - self.date_from
        days = time_delta.days + 1
        self.number_of_days = days if days > 0 else 0

    @api.multi
    def extend_holidays(self):
        self.holidays_id.write({"request_date_to": self.date_to})
        self.holidays_id._onchange_request_parameters()
        self.holidays_id._remove_resource_leave()
        self.holidays_id._create_resource_leave()

        action = {
            "type": "ir.actions.act_window",
            "name": self.holidays_id.display_name,
            "res_model": "hr.leave",
            "res_id": self.holidays_id.id,
            "view_mode": "form",
        }
        return action
