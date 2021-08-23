# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.resource.models.resource import float_to_time
from odoo.addons.hr_holidays.models.hr_leave import DummyAttendance

from dateutil import tz
from pytz import timezone, utc, UTC


class HrLeave(models.Model):
    _inherit = "hr.leave"
    _order = "create_date desc"

    def _default_employee(self):
        return self.env["hr.employee"].search(
            [("user_id", "=", self.env.user.id)], limit=1
        )

    employee_id = fields.Many2one(
        required=True, default=lambda self: self._default_employee()
    )
    description = fields.Text(
        related="holiday_status_id.description",
        readonly=True,
        string="Leave Type Description",
    )

    date_from_custom = fields.Datetime()
    date_to_custom = fields.Datetime()

    department_id = fields.Many2one(
        related="employee_id.department_id", readonly=True, store=True
    )

    tree_color = fields.Char(compute="_compute_color", store=True)

    @api.depends("state")
    def _compute_color(self):
        for record in self:
            if record.state == "validate":
                record.tree_color = "#e2ffe6"
            elif record.state == "validate1":
                record.tree_color = "#e2f0ff"
            elif record.state == "refuse":
                record.tree_color = "#ffefef"
            else:
                record.tree_color = "#ffffff"

    @api.onchange("leave_type_request_unit")
    def _onchange_leave_type_request_unit(self):
        for record in self:
            hours = record.leave_type_request_unit == "hour"
            record.request_unit_hours = hours
            if hours and record.date_from and record.date_to:
                record.date_from_custom = record.date_from
                record.date_to_custom = record.date_to

    ####################################################
    # Overriding methods
    ####################################################

    # Was giving problems with mail_activity_team module
    def activity_update(self):
        return super(
            HrLeave, self.with_context(default_team_id=False)
        ).activity_update()

    # https://github.com/odoo/odoo/blob/12.0/addons/hr_holidays/models/hr_leave.py#L628
    def _validate_leave_request(self):
        """ Validate leave requests (holiday_type='employee')
        by creating a calendar event and a resource leaves. """
        holidays = self.filtered(
            lambda request: request.holiday_type == "employee"
        )
        holidays._create_resource_leave()

    def _get_number_of_days(self, date_from, date_to, employee_id):
        utz = tz.gettz(self.env.user.tz)

        from_dt = (
            fields.Datetime.from_string(date_from)
            .replace(tzinfo=utc)
            .astimezone(utz)
            .replace(tzinfo=None)
        )
        to_dt = (
            fields.Datetime.from_string(date_to)
            .replace(tzinfo=utc)
            .astimezone(utz)
            .replace(tzinfo=None)
        )

        time_delta = to_dt - from_dt
        days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
        return days if days > 0 else 0

    @api.onchange(
        "request_date_from_period",
        "request_hour_from",
        "request_hour_to",
        "date_from_custom",
        "date_to_custom",
        "request_date_from",
        "request_date_to",
        "employee_id",
    )
    def _onchange_request_parameters(self):
        if not self.request_date_from:
            self.date_from = False
            return

        if self.request_unit_hours:
            self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return

        calendar = self.employee_id.resource_calendar_id.id or (
            self.env.user.company_id.resource_calendar_id.id
        )
        domain = [("calendar_id", "=", calendar)]
        attendances = self.env["resource.calendar.attendance"].read_group(
            domain,
            [
                "ids:array_agg(id)",
                "hour_from:min(hour_from)",
                "hour_to:max(hour_to)",
                "dayofweek",
                "day_period",
            ],
            ["dayofweek", "day_period"],
            lazy=False,
        )

        # Must be sorted by dayofweek ASC and day_period DESC
        attendances = sorted(
            [
                DummyAttendance(
                    group["hour_from"],
                    group["hour_to"],
                    group["dayofweek"],
                    group["day_period"],
                )
                for group in attendances
            ],
            key=lambda att: (att.dayofweek, att.day_period != "morning"),
        )

        default_value = DummyAttendance(0, 0, 0, "morning")

        # find first attendance coming after first_day
        attendance_from = next(
            (
                att
                for att in attendances
                if int(att.dayofweek) >= self.request_date_from.weekday()
            ),
            attendances[0] if attendances else default_value,
        )

        # find last attendance coming before last_day
        attendance_to = next(
            (
                att
                for att in reversed(attendances)
                if int(att.dayofweek) <= self.request_date_to.weekday()
            ),
            attendances[-1] if attendances else default_value,
        )

        if self.request_unit_hours:
            self.date_from = self.date_from_custom
            self.date_to = self.date_to_custom
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)
            timez = (
                self.env.user.tz
                if (self.env.user.tz and not self.request_unit_custom)
                else "UTC"
            )  # custom -> already in UTC
            self.date_from = (
                timezone(timez)
                .localize(datetime.combine(self.request_date_from, hour_from))
                .astimezone(UTC)
                .replace(tzinfo=None)
            )
            self.date_to = (
                timezone(timez)
                .localize(datetime.combine(self.request_date_to, hour_to))
                .astimezone(UTC)
                .replace(tzinfo=None)
            )
        self._onchange_leave_dates()

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env["hr.employee"].search(
            [("user_id", "=", self.env.uid)], limit=1
        )
        is_officer = self.env.user.has_group(
            "hr_holidays.group_hr_holidays_user"
        )
        is_manager = self.env.user.has_group(
            "hr_holidays.group_hr_holidays_manager"
        )
        for holiday in self:
            val_type = holiday.holiday_status_id.validation_type
            if state == "confirm":
                continue

            if state == "draft":
                if holiday.employee_id != current_employee and not is_manager:
                    raise UserError(
                        _(
                            "Only a Leave Manager can reset other people leaves."
                        )
                    )
                continue

            if not is_officer:
                raise UserError(
                    _(
                        "Only a Leave Officer or Manager can approve or refuse leave requests."
                    )
                )

            if is_officer:
                # use ir.rule based first access check: department, members, ... (see security.xml)
                holiday.check_access_rule("write")

            if (state == "validate1" and val_type == "both") or (
                state == "validate" and val_type == "manager"
            ):
                manager = (
                    holiday.employee_id.parent_id
                    or holiday.employee_id.department_id.manager_id
                )
                if (
                    manager and manager != current_employee
                ) and not self.env.user.has_group(
                    "hr_holidays.group_hr_holidays_manager"
                ):
                    raise UserError(
                        _(
                            "You must be either %s's manager or Leave manager to approve this leave"
                        )
                        % (holiday.employee_id.name)
                    )

            if state == "validate" and val_type == "both":
                if not self.env.user.has_group(
                    "hr_holidays.group_hr_holidays_manager"
                ):
                    raise UserError(
                        _(
                            "Only an Leave Manager can apply the second approval on leave requests."
                        )
                    )


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"
    _order = "id desc"
