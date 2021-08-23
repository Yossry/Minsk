# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHRContractCAE(TransactionCase):
    def setUp(self):
        super(TestHRContractCAE, self).setUp()
        self.employee = self.browse_ref("hr.employee_al")
        self.cdi = self.browse_ref("hr_cae_contract.hr_contract_type_cdi")
        self.cape_renewal = self.browse_ref(
            "hr_cae_contract.hr_contract_type_cape_renewal"
        )
        self.termination = self.browse_ref(
            "hr_cae_contract.hr_contract_type_termination"
        )
        self.contract = self.env["hr.contract"].create(
            {
                "employee_id": self.employee.id,
                "type_id": self.cdi.id,
                "hours": 40,
                "hourly_wage": 20,
            }
        )

    def test_contract_values(self):
        self.assertEquals(self.contract.amendment_index, 0)
        self.assertEquals(self.contract.wage, 40 * 20)
        #  Todo: add date manipulation test

    def test_amendment(self):
        # Create first 'CAPE extension' amendment
        wizard_1 = (
            self.env["hr.contract.amendment.wizard"]
            .with_context({"active_id": self.contract.id})
            .create(
                {
                    "contract_id": self.contract.id,
                    "type_id": self.cape_renewal.id,
                }
            )
        )
        amendment_1_id = wizard_1.create_amendment()["res_id"]
        amendment_1 = self.env["hr.contract"].browse(amendment_1_id)

        self.assertEquals(amendment_1.echelon, "amendment")
        self.assertEquals(amendment_1.initial_contract_id, self.contract)
        self.assertEquals(amendment_1.amendment_index, 1)
        self.assertEquals(amendment_1.parent_contract_id, self.contract)

        # Create second 'CAPE extension' amendment
        wizard_2 = (
            self.env["hr.contract.amendment.wizard"]
            .with_context({"active_id": amendment_1.id})
            .create(
                {
                    "contract_id": self.contract.id,
                    "type_id": self.cape_renewal.id,
                }
            )
        )
        amendment_2_id = wizard_2.create_amendment()["res_id"]
        amendment_2 = self.env["hr.contract"].browse(amendment_2_id)

        self.assertEquals(amendment_2.echelon, "amendment")
        self.assertEquals(amendment_2.initial_contract_id, self.contract)
        self.assertEquals(amendment_2.amendment_index, 2)
        self.assertEquals(amendment_2.parent_contract_id, amendment_1)

        # check that no third 'CAPE extension' amendment can be made
        self.assertEquals(self.cape_renewal.max_usage, 2)
        self.assertEquals(amendment_2.type_count, 2)
        with self.assertRaises(ValidationError):
            wizard_3 = (
                self.env["hr.contract.amendment.wizard"]
                .with_context({"active_id": amendment_2.id})
                .create(
                    {
                        "contract_id": self.contract.id,
                        "type_id": self.cape_renewal.id,
                    }
                )
            )
            wizard_3.create_amendment()

    def test_termination(self):
        wizard_1 = (
            self.env["hr.contract.amendment.wizard"]
            .with_context({"active_id": self.contract.id})
            .create(
                {
                    "contract_id": self.contract.id,
                    "type_id": self.cape_renewal.id,
                }
            )
        )
        amendment_1_id = wizard_1.create_amendment()["res_id"]
        amendment_1 = self.env["hr.contract"].browse(amendment_1_id)

        termination_1_id = self.contract.create_termination()["res_id"]
        termination_1 = self.env["hr.contract"].browse(termination_1_id)

        termination_1.state = "open"
        self.assertEquals(amendment_1.state, "termination")
