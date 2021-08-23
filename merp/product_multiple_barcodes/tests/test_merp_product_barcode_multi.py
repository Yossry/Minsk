# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestMerpProductBarcodeMulti(TransactionCase):

    def setUp(self):
        super(TestMerpProductBarcodeMulti, self).setUp()
        barcode_1 = self.env['barcode.multi'].create({
            'name': 'test001'
        })
        barcode_2 = self.env['barcode.multi'].create({
            'name': 'test002'
        })
        self.product_1 = self.env['product.template'].create({
            'name': 'product_1',
            'barcode': 'test003',
            'barcode_ids': [(4, barcode_1.id)]
        })
        self.product_2 = self.env['product.template'].create({
            'name': 'product_2',
            'barcode_ids': [(4, barcode_2.id)]
        })

    def test_search_by_barcode_multi_product_1(self):
        results = self.env['product.product']._name_search('test001')
        for res in results:
            self.assertEqual(res[1], 'product_1')

    def test_search_by_barcode_product_1(self):
        results = self.env['product.product']._name_search('test003')
        for res in results:
            self.assertEqual(res[1], 'product_1')

    def test_search_by_barcode_multi_product_2(self):
        results = self.env['product.product']._name_search('test002')
        for res in results:
            self.assertEqual(res[1], 'product_2')
