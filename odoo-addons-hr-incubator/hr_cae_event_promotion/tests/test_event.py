# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import tests


class TestEvent(tests.common.TransactionCase):
    def test_button_register_promotion(self):
        event = self.browse_ref("event.event_0")
        promotion = self.browse_ref("hr_cae_promotion.hr_promotion_test")
        employee_1 = self.browse_ref("hr.employee_al")
        employee_2 = self.browse_ref("hr.employee_mit")

        promotion.spots_max = 2
        employee_1.promotion_id = promotion
        employee_2.promotion_id = promotion
        event.promotion_id = promotion

        seats_before = event.seats_expected
        event.button_register_promotion()
        seats_after = event.seats_expected
        self.assertEqual(seats_after - seats_before, 2)
