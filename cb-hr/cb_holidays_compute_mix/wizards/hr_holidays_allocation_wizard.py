# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrHolidaysAllocationWizard(models.TransientModel):

    _name = "hr.holidays.allocation.wizard"
    _description = "hr.holidays.allocation.wizard"

    name = fields.Char(string="Description")
    holiday_status_id = fields.Many2one(
        "hr.leave.type",
        string="Leave Type",
        required=True,
        domain=[("allocation_type", "!=", "no")],
    )
    duration = fields.Float(string="Duration", required=True)
    employee_ids = fields.Many2many(
        "hr.employee", string="Employees", required=True
    )
    second_validation = fields.Boolean(
        related="holiday_status_id.double_validation", readonly=True
    )
    request_unit = fields.Selection(
        [("day", "Day"), ("hour", "Hours")],
        related="holiday_status_id.request_unit",
    )
    approve = fields.Boolean(string="Automatically Approve", default=True)
    department_id = fields.Many2one("hr.department", string="Department")
    category_id = fields.Many2one("hr.employee.category", string="Tag")

    def _prepare_employee_domain(self):
        res = []
        if self.category_id:
            res.append(("category_ids", "=", self.category_id.id))
        if self.department_id:
            res.append(("department_id", "child_of", self.department_id.id))
        return res

    @api.multi
    def populate(self):
        domain = self._prepare_employee_domain()
        employees = self.env["hr.employee"].search(domain)
        self.employee_ids = employees
        action = {
            "name": _("Create Allocations"),
            "type": "ir.actions.act_window",
            "res_model": "hr.holidays.allocation.wizard",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
            "context": self._context,
        }
        return action

    @api.multi
    def create_allocations(self):
        self.ensure_one()
        for employee in self.employee_ids:
            allocation = self.env["hr.leave.allocation"].create(
                {
                    "name": self.name,
                    "holiday_status_id": self.holiday_status_id.id,
                    "holiday_type": "employee",
                    "employee_id": employee.id,
                    "department_id": employee.department_id.id,
                    "number_of_days": self.duration,
                }
            )

            if self.approve:
                allocation.action_approve()
                if self.second_validation:
                    allocation.action_validate()
        action = self.env.ref(
            "cb_holidays_compute_mix.action_open_all_allocations"
        )
        result = action.read()[0]
        return result

    @api.constrains("duration")
    def check_negative_duration(self):
        for record in self:
            if record.duration <= 0:
                raise ValidationError(_("Duration must be greater than 0"))
