# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHRCAE(TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee_1 = self.env.ref("hr.employee_al")
        self.employee_2 = self.env.ref("hr.employee_mit")
        self.applicant_1 = self.env.ref("hr_recruitment.hr_case_salesman0")
        self.promotion = self.env.ref("hr_cae_promotion.hr_promotion_test")
        self.assertEquals(self.promotion.spots_max, 1)

    def test_create_employee_from_applicant(self):
        self.applicant_1.promotion_id = self.promotion

        self.assertTrue(self.applicant_1 in self.promotion.applicant_ids)

        self.applicant_1.create_employee_from_applicant()
        employee = self.applicant_1.emp_id

        self.assertEquals(employee.promotion_id, self.applicant_1.promotion_id)

        self.assertTrue(employee in self.promotion.employee_ids)
        self.assertTrue(self.applicant_1 not in self.promotion.applicant_ids)

    def test_promotion_spots_max_add_employee(self):
        self.employee_1.promotion_id = self.promotion

        with self.assertRaises(ValidationError):
            self.employee_2.promotion_id = self.promotion

    def test_promotion_spots_max_create_employee_from_applicant(self):
        self.employee_1.promotion_id = self.promotion

        self.applicant_1.promotion_id = self.promotion
        self.assertFalse(self.applicant_1.emp_id)
        with self.assertRaises(ValidationError):
            self.applicant_1.create_employee_from_applicant()

    def test_promotion_spots_max_reset_regime(self):
        self.employee_1.promotion_id = self.promotion

        self.promotion.spots_regime = "unlimited"
        self.employee_2.promotion_id = self.promotion

        with self.assertRaises(ValidationError):
            self.promotion.spots_regime = "limited"
