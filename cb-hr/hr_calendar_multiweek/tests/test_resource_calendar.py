# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import datetime, timedelta
from pytz import timezone


class TestResourceCalendar(TransactionCase):
    def setUp(self):
        super().setUp()
        self.calendar = self.env["resource.calendar"].create(
            {"name": "Test calendar 1", "attendance_ids": []}
        )
        self.attendance_01 = self.env["resource.calendar.attendance"].create(
            {
                "name": "1",
                "dayofweek": "0",
                "hour_from": 8,
                "hour_to": 12,
                "date_from": False,
                "calendar_id": self.calendar.id,
            }
        )
        self.attendance_02 = self.env["resource.calendar.attendance"].create(
            {
                "name": "2",
                "dayofweek": "0",
                "hour_from": 13,
                "hour_to": 14,
                "date_from": False,
                "calendar_id": self.calendar.id,
            }
        )
        self.attendance_03 = self.env["resource.calendar.attendance"].create(
            {
                "name": "2",
                "dayofweek": "1",
                "hour_from": 13,
                "hour_to": 14,
                "date_from": False,
                "calendar_id": self.calendar.id,
            }
        )
        today = fields.Date.today()
        timez = timezone(self.env.user.tz)
        self.date = today + timedelta(days=-(today.weekday()))
        self.start_date = datetime.combine(self.date, datetime.min.time())
        self.start_date = timez.localize(self.start_date)
        self.end_date = datetime.combine(self.date, datetime.max.time())
        self.end_date = timez.localize(self.end_date)

    def test_onchange(self):
        attendance = self.env["resource.calendar.attendance"].new(
            {
                "name": "1",
                "dayofweek": "0",
                "hour_from": 8,
                "hour_to": 12,
                "date_from": False,
                "calendar_id": self.calendar.id,
            }
        )
        attendance.calendar_week_number = 2
        attendance.week_number = 2
        attendance.calendar_week_number = 1
        attendance._onchange_calendar_week_number()
        self.assertEqual(1, attendance.week_number)

    def test_standard_behaviour(self):
        intervals = self.calendar._work_intervals(
            self.start_date, self.end_date
        )
        attendances = [interval[2].id for interval in intervals]

        self.assertIn(self.attendance_01.id, attendances)
        self.assertIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        monday_start = self.start_date + timedelta(days=7)
        monday_end = self.end_date + timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertIn(self.attendance_01.id, attendances)
        self.assertIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)

    def test_week_behaviour_01(self):
        monday_start = self.start_date
        monday_end = self.end_date
        self.attendance_01.calendar_week_number = 2
        self.attendance_02.calendar_week_number = 2
        self.attendance_03.calendar_week_number = 2
        if divmod(monday_start.isocalendar()[1], 2)[1] == 0:
            monday_start = self.start_date + timedelta(days=7)
            monday_end = self.end_date + timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertIn(self.attendance_01.id, attendances)
        self.assertIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        monday_start += timedelta(days=7)
        monday_end += timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]

        self.assertNotIn(self.attendance_01.id, attendances)
        self.assertNotIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)

    def test_week_behaviour_02(self):
        monday_start = self.start_date
        monday_end = self.end_date
        self.attendance_01.calendar_week_number = 2
        self.attendance_02.calendar_week_number = 2
        self.attendance_03.calendar_week_number = 2
        self.attendance_02.week_number = 2
        if divmod(monday_start.isocalendar()[1], 2)[1] == 0:
            monday_start = self.start_date + timedelta(days=7)
            monday_end = self.end_date + timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertIn(self.attendance_01.id, attendances)
        self.assertNotIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        monday_start += timedelta(days=7)
        monday_end += timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertNotIn(self.attendance_01.id, attendances)
        self.assertIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)

    def test_week_behaviour_03(self):
        monday_start = self.start_date
        monday_end = self.end_date
        self.attendance_01.calendar_week_number = 3
        self.attendance_02.calendar_week_number = 3
        self.attendance_03.calendar_week_number = 3
        self.attendance_02.week_number = 2
        self.attendance_03.week_number = 3
        if divmod(monday_start.isocalendar()[1], 3)[1] == 0:
            monday_start += timedelta(days=7)
            monday_end += timedelta(days=7)
        if divmod(monday_start.isocalendar()[1], 3)[1] == 2:
            monday_start += timedelta(days=14)
            monday_end += timedelta(days=14)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertIn(self.attendance_01.id, attendances)
        self.assertNotIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        monday_start += timedelta(days=7)
        monday_end += timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertNotIn(self.attendance_01.id, attendances)
        self.assertIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        monday_start += timedelta(days=7)
        monday_end += timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertNotIn(self.attendance_01.id, attendances)
        self.assertNotIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        intervals = self.calendar._work_intervals(
            monday_start + timedelta(days=1), monday_end + timedelta(days=1)
        )
        attendances = [interval[2].id for interval in intervals]
        self.assertNotIn(self.attendance_01.id, attendances)
        self.assertNotIn(self.attendance_02.id, attendances)
        self.assertIn(self.attendance_03.id, attendances)

    def test_week_behaviour_04(self):
        monday_start = self.start_date
        monday_end = self.end_date
        self.attendance_01.calendar_week_number = 3
        self.attendance_02.calendar_week_number = 3
        self.attendance_03.calendar_week_number = 3
        self.attendance_01.date_from = monday_start.date()
        self.attendance_02.date_from = monday_start.date()
        self.attendance_03.date_from = monday_start.date()
        self.attendance_01.week_number = 1
        self.attendance_02.week_number = 2
        self.attendance_03.week_number = 3
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertIn(self.attendance_01.id, attendances)
        self.assertNotIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        monday_start += timedelta(days=7)
        monday_end += timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertNotIn(self.attendance_01.id, attendances)
        self.assertIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        monday_start += timedelta(days=7)
        monday_end += timedelta(days=7)
        intervals = self.calendar._work_intervals(monday_start, monday_end)
        attendances = [interval[2].id for interval in intervals]
        self.assertNotIn(self.attendance_01.id, attendances)
        self.assertNotIn(self.attendance_02.id, attendances)
        self.assertNotIn(self.attendance_03.id, attendances)
        intervals = self.calendar._work_intervals(
            monday_start + timedelta(days=1), monday_end + timedelta(days=1)
        )
        attendances = [interval[2].id for interval in intervals]
        self.assertNotIn(self.attendance_01.id, attendances)
        self.assertNotIn(self.attendance_02.id, attendances)
        self.assertIn(self.attendance_03.id, attendances)

    def test_week_behaviour_05(self):
        self.env["resource.calendar.attendance"].create(
            {
                "name": "1",
                "dayofweek": "3",
                "hour_from": 8,
                "hour_to": 12,
                "calendar_week_number": 2,
                "week_number": 1,
                "date_from": False,
                "calendar_id": self.calendar.id,
            }
        )
        self.env["resource.calendar.attendance"].create(
            {
                "name": "2",
                "dayofweek": "3",
                "hour_from": 11,
                "hour_to": 15,
                "calendar_week_number": 2,
                "week_number": 2,
                "date_from": False,
                "calendar_id": self.calendar.id,
            }
        )
        date_start = self.start_date + timedelta(days=3)
        date_end = self.end_date + timedelta(days=3)
        self.calendar.refresh()
        intervals = self.calendar._work_intervals(date_start, date_end)
        self.assertEqual(1, len(intervals))
        for start, stop, meta in intervals:
            self.assertEqual(len(meta), 1)
            self.assertEqual(4, (stop - start).seconds / 3600)
