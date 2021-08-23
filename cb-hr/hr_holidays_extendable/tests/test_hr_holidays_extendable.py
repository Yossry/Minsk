# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestHrHolidaysExtendable(TransactionCase):
    def setUp(self):
        super(TestHrHolidaysExtendable, self).setUp()
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner",
                "company_id": False,
                "is_practitioner": True,
            }
        )
        self.employee = self.env["hr.employee"].create(
            {"name": "Employee 1", "partner_id": self.partner.id}
        )
        self.holiday_type = self.env["hr.leave.type"].create(
            {
                "name": "Leave Type Test",
                "extendable": True,
                "allocation_type": "fixed",
                "validity_start": False,
            }
        )
        self.allocation = self.env["hr.leave.allocation"].create(
            {
                "name": "Test",
                "employee_id": self.employee.id,
                "holiday_status_id": self.holiday_type.id,
                "number_of_days": 10,
            }
        )
        self.allocation.action_validate()

    def test_hr_holidays_extendable(self):
        holiday = self.env["hr.leave"].create(
            {
                "name": "Test",
                "employee_id": self.employee.id,
                "holiday_status_id": self.holiday_type.id,
                "request_date_from": "2019-05-21",
                "request_date_to": "2019-05-22",
            }
        )
        holiday._onchange_request_parameters()
        holiday.action_validate()
        remaining_days = self.holiday_type.get_days(self.employee.id)[
            self.holiday_type.id
        ]["remaining_leaves"]
        self.assertEqual(remaining_days, 8)

        wizard = (
            self.env["wizard.extend.holidays"]
            .with_context({"active_id": holiday.id})
            .create({})
        )
        self.assertEqual(wizard.holidays_id.id, holiday.id)
        wizard.write({"date_to": "2019-05-23"})
        wizard.extend_holidays()

        self.assertEqual(
            fields.Date.to_string(holiday.request_date_to), "2019-05-23"
        )
        self.assertEqual(holiday.number_of_days, 3)
        remaining_days = self.holiday_type.get_days(self.employee.id)[
            self.holiday_type.id
        ]["remaining_leaves"]
        self.assertEqual(remaining_days, 7)
