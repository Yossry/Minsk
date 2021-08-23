# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.resource.models.resource import Intervals
from pytz import timezone, UTC


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def get_duty_shift_domain(self, start, end):
        """
        returns the domain of the duties that cross whith a range. It should be
        the duties that begins before the range ends and ends after the range
        starts
        :param start: datetime
        :param end: datetime
        :return: a domain
        """
        return [
            ("employee_id", "=", self.env.context.get("employee_id")),
            ("start_date", "<=", fields.Datetime.to_string(end)),
            ("end_date", ">=", fields.Datetime.to_string(start)),
        ]

    def get_duty_shift_intervals(self, start_dt, end_dt, resource=None):
        tz = timezone((resource or self).tz)
        search_start = start_dt.astimezone(UTC).replace(tzinfo=None)
        search_end = end_dt.astimezone(UTC).replace(tzinfo=None)
        intervals_list = []
        shifts = self.env["hr.duty.shift"].search(
            self.get_duty_shift_domain(search_start, search_end)
        )
        # The affected shifts are added as new intervals.
        for shift in shifts:
            dt_f = max(start_dt, tz.localize(shift.start_date))
            dt_t = min(end_dt, tz.localize(shift.end_date))
            intervals_list.append(
                (dt_f, dt_t, self.env["resource.calendar.attendance"])
            )
        return Intervals(intervals_list)

    def _work_intervals(self, start_dt, end_dt, resource=None, domain=None):
        intervals = super()._work_intervals(start_dt, end_dt, resource, domain)
        if self.env.context.get("employee_id", False):
            shifts = self.get_duty_shift_intervals(start_dt, end_dt, resource)
            intervals |= shifts
        return intervals

    @api.model
    def _interval_remove_leaves(self, interval, leave_intervals):
        # The shifts should not be affected by the holidays.
        # TODO: Shifts should be affected by the leaves?
        if "shifts" in interval.data and interval.data["shifts"]:
            return super()._interval_remove_leaves(interval, [])
        return super()._interval_remove_leaves(interval, leave_intervals)
