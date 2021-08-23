# Copyright 2019 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import unittest
from odoo.tests import common, tagged


class TestMapper(common.TransactionCase):

    # This needs to be work carefully, for ensure the properly work of the module
    def setUp(self):
        super(TestMapper, self).setUp()
        self.Mapper = self.env['webservice.mapper']
        self.Model = self.env['ir.model'].search([
            'model', '=', 'ir.model',
        ])
        self.FieldMapper = self.env['webservice.mapper.fields']
        self.Field = self.env['ir.model.fields']

        self.Mapper = self.Mappper.create({
            'name': 'Test Fields',
            'odoo_model': self.Model.id,
            'source_mode': 'ir.model'
        })
        self.field1 = self.Field.search([
            ('model', '=', 'ir.model'),
            ('name', '=', 'count')
        ])
        self.field2 = self.Field.search([
            ('model', '=', 'ir.model'),
            ('name', '=', 'info')
        ])
        self.Mapper.write({
            'mapper_fields_ids', [(0, 0, {
                'odoo_field': self.field1.id
            })]
        })
        self.Mapper.write({
            'mapper_fields_ids', [(0, 0, {
                'odoo_field': self.field2.id,
                'source_field': 'info_test'
            })]
        })
        self.Mapper.write({
            'mapper_fields_ids', [(0, 0, {
                'odoo_field': self.field2.id,
                'source_field': 'fail_field'
            })]
        })

    def test_fail(self):
        self.assertEqual(1, 2, msg="FAILED IN 1=2")

    def test_check_mapped_fields(self):
        """ Checks if the _check_mapped_fields works properly
        """
        field_list = ['count', 'info_test']
        self.Mapper._check_mapped_fields(field_list)
        self.assertEqual(
            self.Mapper.mapper_fields_ids[0].state_valid, 'valid')
        self.assertEqual(
            self.Mapper.mapper_fields_ids[1].state_valid, 'valid')
        self.assertEqual(
            self.Mapper.mapper_fields_ids[2].state_valid, 'not_valid')
