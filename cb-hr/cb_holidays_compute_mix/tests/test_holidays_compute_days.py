# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from datetime import datetime


class TestHolidaysComputeDays(common.TransactionCase):
    def setUp(self):
        super(TestHolidaysComputeDays, self).setUp()
        self.HrHolidays = self.env["hr.leave"]
        self.calendar = self.env["resource.calendar"].create(
            {"name": "Calendar", "attendance_ids": []}
        )
        for day in range(5):  # From monday to friday
            self.calendar.attendance_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "08",
                        "hour_to": "12",
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "14",
                        "hour_to": "18",
                    },
                ),
            ]
        self.employee = self.env["hr.employee"].create(
            {"name": "Employee 1", "resource_calendar_id": self.calendar.id}
        )
        self.holiday_type = self.env["hr.leave.type"].create(
            {"name": "Leave Type Test", "allocation_type": "no"}
        )
        self.holiday_type_hours = self.env["hr.leave.type"].create(
            {
                "name": "Leave Type Test",
                "request_unit": "hour",
                "allocation_type": "no",
            }
        )
        # Remove timezone for controlling data better
        self.env.user.tz = False

    def test_compute_dates(self):
        holidays = self.HrHolidays.new(
            {
                "request_date_from": "1946-12-20",
                "request_date_to": "1946-12-21",
                "holiday_status_id": self.holiday_type.id,
                "employee_id": self.employee.id,
            }
        )
        holidays._onchange_request_parameters()
        self.assertEqual(holidays.number_of_days, 2)
        self.assertEqual(holidays.date_from, datetime(1946, 12, 20, 8, 0))
        self.assertEqual(holidays.date_to, datetime(1946, 12, 21, 18, 0))

        holidays = self.HrHolidays.new(
            {
                "date_from_custom": "1946-12-26 09:00:00",
                "date_to_custom": "1946-12-26 20:00:00",
                "request_date_from": "1946-12-26",
                "request_date_to": "1946-12-26",
                "holiday_status_id": self.holiday_type_hours.id,
                "leave_type_request_unit": "hour",
                "employee_id": self.employee.id,
            }
        )
        holidays._onchange_leave_type_request_unit()
        holidays._onchange_request_parameters()

        holidays._compute_number_of_hours_display()
        self.assertEqual(holidays.date_from, datetime(1946, 12, 26, 9, 0))
        self.assertEqual(holidays.number_of_hours_display, 6)
