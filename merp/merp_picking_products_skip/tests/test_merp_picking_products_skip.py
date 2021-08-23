# Copyright 2019 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from datetime import datetime


class TestMerpPickingProductsSkip(TransactionCase):

    def setUp(self):
        super(TestMerpPickingProductsSkip, self).setUp()
        self.location_1 = self.env['stock.location'].create({
            'name': 'test_location_1',
            'removal_prio': 2
        })
        self.location_2 = self.env['stock.location'].create({
            'name': 'test_location_2',
            'removal_prio': 3
        })
        company = self.env.user.company_id
        picking_type = self.env['stock.picking.type'].search([], limit=1)
        self.stock_picking = self.env['stock.picking'].create({
            'name': 'test_stock_picking',
            'location_id': self.location_1.id,
            'location_dest_id': self.location_2.id,
            'move_type': 'one',
            'company_id': company.id,
            'picking_type_id': picking_type.id
        })
        product_uom = self.env['uom.uom'].search([], limit=1, order='id')
        products = self.env['product.template'].search([], limit=2)
        self.move_line_1 = self.env['stock.move.line'].create({
            'picking_id': self.stock_picking.id,
            'qty_done': 1.0,
            'location_id': self.location_1.id,
            'date': datetime.now(),
            'location_dest_id': self.location_2.id,
            'product_uom_qty': 20.0,
            'product_uom_id': product_uom.id,
            'product_id': products[0].id,
            'skipped': False
        })
        self.move_line_2 = self.env['stock.move.line'].create({
            'picking_id': self.stock_picking.id,
            'qty_done': 2.0,
            'location_id': self.location_2.id,
            'date': datetime.now(),
            'location_dest_id': self.location_1.id,
            'product_uom_qty': 25.0,
            'product_uom_id': product_uom.id,
            'product_id': products[1].id,
            'skipped': True
        })

    def test_module_install_check(self):
        module = self.env['ir.module.module'].search([('name', '=', 'merp_outgoing_routing')])
        if module:
            self.assertEqual(len(self.stock_picking.operations_to_pick), 1)
