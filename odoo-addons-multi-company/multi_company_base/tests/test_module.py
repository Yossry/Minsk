# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from ..fix_test import fix_required_field


class TestModule(TransactionCase):
    """Tests for 'Multi Company - Base' Module"""

    # Overload Section
    def setUp(self):
        super(TestModule, self).setUp()

        self.user_obj = self.env['res.users']
        self.company_obj = self.env['res.company']
        self.demo_user = self.env.ref('base.user_demo')
        self.main_company = self.env.ref('base.main_company')
        fix_required_field(self, 'DROP')

    def tearDown(self):
        self.cr.rollback()
        fix_required_field(self, 'SET')
        super(TestModule, self).tearDown()

    # Test Section
    def test_01_unlink_user_to_company(self):
        """[Functional Test] Test if unlinking user from company
        check if the user is currently logged into this company"""
        new_company = self.company_obj.create({'name': 'Company Test'})
        # Add demo users to main and new company
        self.demo_user.write({
            'company_ids': [new_company.id, self.main_company.id],
        })

        no_demo_user_ids = [(
            6, False,
            [x.id for x in self.main_company.user_ids if x != self.demo_user])]

        # Remove the non current company to the demo user, should work
        new_company.user_ids = no_demo_user_ids

        # Add demo users to main and new company
        self.demo_user.write({
            'company_ids': [new_company.id, self.main_company.id],
        })

        # Remove the current company to the demo user, should work
        with self.assertRaises(ValidationError):
            self.main_company.user_ids = no_demo_user_ids
