# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestHrPartner(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHrPartner, cls).setUpClass()
        cls.employee_model = cls.env['hr.employee']
        cls.partner_model = cls.env['res.partner']
        cls.user_model = cls.env['res.users']
        cls.work_email = 'workemail@exampleodoo.edu'
        cls.employee = cls.employee_model.create({
            'name': 'Employee Name',
            'work_email': cls.work_email,
        })

    def test_hr_partner_with_user(self):
        self.user = self.user_model.create({
            'name': 'Employee Name',
            'login': self.work_email,
            'email': self.work_email,
        })
        self.assertFalse(self.employee.address_id)
        self.assertFalse(self.employee.user_id)
        self.employee.button_find_or_create_user_id()
        self.assertEquals(self.employee.user_id, self.user)
        self.assertEquals(self.employee.address_id, self.user.partner_id)

    def test_hr_partner_without_user(self):
        self.address = self.partner_model.create({
            'name': self.employee.name,
            'email': self.work_email,
        })
        self.assertFalse(self.employee.address_id)
        self.assertFalse(self.employee.user_id)
        self.employee.button_find_or_create_address_id()
        self.assertFalse(self.employee.user_id)
        self.assertEquals(self.employee.address_id, self.address)
        self.employee.button_find_or_create_user_id()
        self.user = self.user_model.search([
            ('login', '=', self.work_email)], limit=1)
        self.assertEquals(self.employee.user_id, self.user)
        self.assertEquals(self.employee.address_id, self.user.partner_id)
