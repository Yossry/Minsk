# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.resource.models.resource import float_to_time


class ResourceCalendar(models.Model):

    _inherit = "resource.calendar"

    company_id = fields.Many2one(default=False)
    not_archived = fields.Boolean(default=True)

    @api.multi
    def toggle_archive_calendar(self):
        for record in self:
            record.not_archived = not record.not_archived

    @api.multi
    def _get_day_attendances(self, day_date, start_time, end_time):
        """ Given a day date, return matching attendances. Those can be limited
        by starting and ending time objects. """
        self.ensure_one()
        weekday = day_date.weekday()
        attendances = self.env["resource.calendar.attendance"]

        for attendance in self.attendance_ids.filtered(
            lambda att: int(att.dayofweek) == weekday
            and not (
                att.date_from
                and fields.Date.from_string(att.date_from) > day_date
            )
            and not (
                att.date_to and fields.Date.from_string(att.date_to) < day_date
            )
        ):
            if start_time and float_to_time(attendance.hour_to) < start_time:
                continue
            if end_time and float_to_time(attendance.hour_from) > end_time:
                continue
            attendances |= attendance
        return attendances.filtered(lambda r: r._check_week(day_date))
