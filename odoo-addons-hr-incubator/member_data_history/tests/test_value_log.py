# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import tests


@tests.tagged("access_rights")
class TestValueLog(tests.common.TransactionCase):
    def setUp(self):

        super(TestValueLog, self).setUp()

        self.employee = self.browse_ref("hr.employee_al")

    def test_log_contract_type_start_end(self):
        contract = self.env["hr.contract"].create(
            {
                "name": "test contract",
                "employee_id": self.employee.id,
                "type_id": self.ref("hr_contract.hr_contract_type_emp"),
                "date_start": "2019-10-12",
                "hours": 7,
                "hourly_wage": 70,
                "wage": 2000,
            }
        )

        contract.date_start = "2019-11-13"
        contract.date_end = "2021-11-23"
        contract.type_id = self.ref("hr_contract.hr_contract_type_wrkr")

        log = self.env["value.log"].search(
            [
                ("model", "=", "hr.contract"),
                ("field", "=", "date_start"),
                ("previous_value", "=", "2019-10-12"),
                ("new_value", "=", "2019-11-13"),
            ]
        )
        self.assertTrue(log)

        log = self.env["value.log"].search(
            [
                ("model", "=", "hr.contract"),
                ("field", "=", "date_end"),
                ("record_id", "=", contract.id),
                ("previous_value", "=", False),
                ("new_value", "=", "2021-11-23"),
            ]
        )
        self.assertTrue(log)

        old_type = self.browse_ref("hr_contract.hr_contract_type_emp")
        new_type = self.browse_ref("hr_contract.hr_contract_type_wrkr")
        log = self.env["value.log"].search(
            [
                ("model", "=", "hr.contract"),
                ("field", "=", "type_id"),
                ("record_id", "=", contract.id),
                ("previous_value", "=", old_type.name),
                ("new_value", "=", new_type.name),
            ]
        )
        self.assertTrue(log)

    def test_log_partner_zip_code(self):
        partner = self.browse_ref("base.res_partner_1")
        old_zip = partner.zip
        partner.zip = "4100"

        log = self.env["value.log"].search(
            [
                ("model", "=", "res.partner"),
                ("field", "=", "zip"),
                ("record_id", "=", partner.id),
                ("previous_value", "=", str(old_zip)),
                ("new_value", "=", "4100"),
            ]
        )
        self.assertTrue(log)

    def test_log_employee_addresses(self):
        employee = self.browse_ref("hr.employee_hne")
        partner = self.browse_ref("base.res_partner_1")

        previous_home_zip = employee.address_home_id.zip
        previous_work_zip = employee.address_id.zip
        employee.address_home_id = partner
        employee.address_id = partner

        log = self.env["value.log"].search(
            [
                ("model", "=", "hr.employee"),
                ("field", "=", "address_home_id.zip"),
                ("record_id", "=", employee.id),
                ("previous_value", "=", previous_home_zip),
                ("new_value", "=", partner.zip),
            ]
        )
        self.assertTrue(log)

        log = self.env["value.log"].search(
            [
                ("model", "=", "hr.employee"),
                ("field", "=", "address_id.zip"),
                ("record_id", "=", employee.id),
                ("previous_value", "=", previous_work_zip),
                ("new_value", "=", partner.zip),
            ]
        )
        self.assertTrue(log)
