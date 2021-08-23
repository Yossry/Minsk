from pytz import timezone, utc
from datetime import datetime, time, timedelta

from odoo import api, fields, models, SUPERUSER_ID
from odoo.addons.resource.models.resource import float_to_time


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    mute_warnings = fields.Boolean(string="Mute Warnings")

    def get_warning_domain(self, date):
        today = fields.Datetime.from_string(date)
        tomorrow = today + timedelta(days=1)
        today = fields.Datetime.to_string(today)
        tomorrow = fields.Datetime.to_string(tomorrow)
        return [
            ("create_date", ">=", today),
            ("create_date", "<", tomorrow),
            ("employee_id", "=", self.id),
        ]

    def _create_warning(self, w_type, date, min_int=False, max_int=False):
        if not self.active or self.mute_warnings:
            return
        warning_obj = self.env["hr.attendance.warning"]
        warning = warning_obj.search(self.get_warning_domain(date), limit=1)
        if warning:
            warning.sudo(user=SUPERUSER_ID).write(
                {
                    "state": "pending",
                    "warning_line_ids": [
                        (
                            0,
                            0,
                            {
                                "warning_type": w_type,
                                "min_int": min_int,
                                "max_int": max_int,
                            },
                        )
                    ],
                }
            )
        else:
            self.env["hr.attendance.warning"].sudo(user=SUPERUSER_ID).create(
                self._create_warning_vals(w_type, min_int, max_int)
            )
        warning_obj.update_counter()

    def _create_warning_vals(self, w_type, min_int=False, max_int=False):
        return {
            "employee_id": self.id,
            "warning_line_ids": [
                (
                    0,
                    0,
                    {
                        "warning_type": w_type,
                        "min_int": min_int,
                        "max_int": max_int,
                    },
                )
            ],
        }

    @api.multi
    def attendance_action_change(self):
        timez = timezone(self.env.user.tz)
        attendance = super(HrEmployee, self).attendance_action_change()
        if attendance:
            action_time = (
                fields.Datetime.from_string(
                    attendance.check_out or attendance.check_in
                )
                .replace(tzinfo=utc)
                .astimezone(timez)
            )
            work_intervals = self.resource_calendar_id._work_intervals(
                datetime.combine(
                    action_time.date(), time(0, 0, 0, 0, tzinfo=timez)
                ),
                datetime.combine(
                    action_time.date(),
                    time(23, 59, 59, 99999, tzinfo=timez),
                ),
                resource=self.resource_id,
            )
            calendar_attendances = self.env['resource.calendar.attendance']
            for start, stop, meta in work_intervals:
                if meta._name == 'resource.calendar.attendance':
                    calendar_attendances |= meta

            intervals = []
            for att in calendar_attendances:
                start = datetime.combine(
                    action_time.date(), float_to_time(att.hour_from)
                ).replace(tzinfo=utc).astimezone(timez)
                stop = datetime.combine(
                    action_time.date(), float_to_time(att.hour_to)
                ).replace(tzinfo=utc).astimezone(timez)
                intervals.append((start, stop, att))

            in_interval = any(
                [
                    start + timedelta(minutes=-meta.margin_from or 0)
                    <= action_time
                    <= stop + timedelta(minutes=meta.margin_to or 0)
                    for start, stop, meta in intervals
                ]
            )
            public_holiday = self.env["hr.holidays.public"].is_public_holiday(
                action_time.date(), self.id
            )

            if not in_interval or public_holiday:
                date = fields.Date.to_string(action_time.date())
                self._create_warning(date=date, w_type="out_of_interval")
        return attendance
