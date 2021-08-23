# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from dateutil.rrule import rrule, DAILY
from pytz import timezone
from datetime import timedelta
from odoo import api, fields, models
from odoo.addons.resource.models.resource import Intervals, float_to_time


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def _attendance_intervals(self, start_dt, end_dt, resource=None):
        intervals = super()._attendance_intervals(
            start_dt, end_dt, resource=resource
        )
        result = []
        combine = datetime.combine

        # express all dates and times in the resource's timezone
        tz = timezone((resource or self).tz)
        start_dt = start_dt.astimezone(tz)
        end_dt = end_dt.astimezone(tz)
        for interval in intervals:
            start, stop, meta = interval
            if meta._name == "resource.calendar.attendance":
                dt = start_dt.date()
                new_meta = meta.filtered(lambda r: r._check_week(dt))
                if new_meta:
                    start = start.date()
                    until = stop.date()
                    for attendance in new_meta:
                        if attendance.date_from:
                            start = max(start, attendance.date_from)
                        if attendance.date_to:
                            until = min(until, attendance.date_to)
                        weekday = int(attendance.dayofweek)
                        for day in rrule(
                            DAILY, start, until=until, byweekday=weekday
                        ):
                            # attendance hours are interpreted in the
                            # resource's timezone
                            dt0 = tz.localize(
                                combine(
                                    day, float_to_time(attendance.hour_from)
                                )
                            )
                            dt1 = tz.localize(
                                combine(day, float_to_time(attendance.hour_to))
                            )
                            result.append(
                                (
                                    max(start_dt, dt0),
                                    min(end_dt, dt1),
                                    attendance,
                                )
                            )
            else:
                result.append(interval)
        return Intervals(result)


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    calendar_week_number = fields.Integer(
        default=1, help="Total number of weeks to use for the rule"
    )
    week_number = fields.Integer(
        default=1, help="Week when the rule must be applied"
    )

    _sql_constraints = [
        (
            "calendar_week_number_consistency",
            "CHECK(calendar_week_number >= 1)",
            "Calendar week number must be greater than 1",
        ),
        (
            "week_number_consistency",
            "CHECK(week_number >= 1)",
            "Week number must be greater than 1",
        ),
        (
            "week_number_consistency_max",
            "CHECK(calendar_week_number >= week_number)",
            "Week number must be less or equal than calendar week number",
        ),
    ]

    @api.onchange("calendar_week_number")
    def _onchange_calendar_week_number(self):
        if self.week_number > self.calendar_week_number:
            self.week_number = self.calendar_week_number

    def _get_week_number(self, day_date):
        if self.date_from:
            weeks = (
                1
                + divmod(
                    (
                        day_date
                        - (
                            self.date_from
                            + timedelta(days=-self.date_from.weekday())
                        )
                    ).days,
                    7,
                )[0]
            )
        else:
            weeks = day_date.isocalendar()[1]
        number = divmod(weeks, self.calendar_week_number)[1]
        if number == 0:
            return self.calendar_week_number
        return number

    def _check_week(self, day_date):
        if not self.calendar_week_number or self.calendar_week_number == 1:
            return True
        return self.week_number == self._get_week_number(day_date)
