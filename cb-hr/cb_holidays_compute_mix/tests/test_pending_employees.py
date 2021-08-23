# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPendingEmployees(TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee1 = self.env["hr.employee"].create({"name": "Employee1"})
        self.employee2 = self.env["hr.employee"].create({"name": "Employee2"})

        self.status1 = self.env["hr.leave.type"].create(
            {
                "name": "Status1",
                "allocation_type": "fixed",
                "validation_type": "hr",
            }
        )
        self.status2 = self.env["hr.leave.type"].create(
            {
                "name": "Status2",
                "allocation_type": "fixed",
                "validation_type": "hr",
            }
        )
        self.wizard = self.env["hr.holidays.pending.employees"].create({})

    def test_pending_employees(self):
        allocation1 = self.env["hr.leave.allocation"].create(
            {
                "holiday_status_id": self.status1.id,
                "number_of_days": 3,
                "employee_id": self.employee1.id,
            }
        )
        allocation1.action_approve()

        allocation2 = self.env["hr.leave.allocation"].create(
            {
                "holiday_status_id": self.status2.id,
                "number_of_days": 3,
                "employee_id": self.employee2.id,
            }
        )
        allocation2.action_approve()

        self.wizard.write({"holiday_status_id": self.status1.id})
        self.wizard._compute_pending_employees()

        self.assertTrue(self.wizard.pending_employees_ids)
        self.assertTrue(
            self.wizard.pending_employees_ids[0].employee_id.name, "Employee 1"
        )
        self.assertTrue(
            self.wizard.pending_employees_ids[0].remaining, "3 days"
        )

        self.wizard.write({"holiday_status_id": self.status2.id})
        self.wizard._compute_pending_employees()

        self.assertTrue(self.wizard.pending_employees_ids)
        self.assertTrue(
            self.wizard.pending_employees_ids[0].employee_id.name, "Employee 2"
        )
        self.assertTrue(
            self.wizard.pending_employees_ids[0].remaining, "3 hours"
        )
        self.wizard.write({"holiday_status_id": False})
        self.wizard._compute_pending_employees()
        self.assertFalse(self.wizard.pending_employees_ids)
