# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    """Tests for 'Product Fiscal Company' Module"""

    # Overload Section
    def setUp(self):
        super(TestModule, self).setUp()
        self.pricelist_obj = self.env['product.pricelist']
        self.wizard_obj = self.env['res.company.create.wizard']
        self.user_erp_manager = self.env.ref(
            'company_wizard_base.user_erp_manager')

    # Test Section
    def test_01_pricelist_creation(self):
        """[Functional Test] creating a new company via wizard,
        with user accountant, should create (or update) a pricelist"""
        wizard = self.wizard_obj.sudo(self.user_erp_manager).create({
            'company_name': 'Test Company Wizard',
            'company_code': 'WIZ',
        })
        wizard.button_create_company()
        pricelists = self.pricelist_obj.search([
            ('company_id', '=', wizard.company_id.id),
            ('name', '=', 'WIZ - Public Pricelist'),
        ])
        self.assertEqual(
            len(pricelists), 1,
            "Create a company by wizard should create a pricelist")
