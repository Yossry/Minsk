# Copyright 2019 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import UserError, Warning
import base64
import csv
from io import StringIO

import logging
_logger = logging.getLogger(__name__)


class ImportMappers(models.TransientModel):
    _name = 'import.mappers'
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string="Files"
    )
    name = fields.Char(string='Filename')
    delimeter = fields.Char(
        string='Delimiter',
        default=',',
        help='Default delimiter ","',
    )

    def search_mapper(self, ref):
        return self.env['webservice.mapper'].search([
            ('ref_code', '=', ref)
        ])

    def create_field(self, model, field_val):
        """Create a fields for a mapper"""
        mapper_field_obj = self.env['webservice.mapper.fields']
        fields_obj = self.env['ir.model.fields']
        field_id = fields_obj.search([
            ('name', '=', field_val['odoo_field']),
            ('model', '=', model),
        ])
        if not field_id:
            if field_val['odoo_field'] == "x_old_id":
                model_obj = self.env['ir.model'].search([
                    ('model', '=', model)
                ]),
                field_id = field_id.sudo().create({
                    'name': 'x_old_id',
                    'field_description': 'Old ID',
                    'model': model,
                    'model_id': model_obj[0].id,
                    'ttype': 'integer',
                    'store': True,
                    'index': True,
                    'state': 'manual'
                })
            else:
                raise UserError('Field %s from model %s not found' %
                                (field_val['odoo_field'], model))
                return None
        field_val['odoo_field'] = field_id.id
        if field_val['dependence_ref'] != 'False':
            mapper_id = self.search_mapper(field_val['dependence_ref'])
            if mapper_id:
                field_val['dependence_id'] = mapper_id.id
            field_val['dependence_ref_code'] = field_val['dependence_ref']
        field_val.pop('dependence_ref')
        field_val['unique'] = eval(field_val['unique'])
        mapper_field_obj = mapper_field_obj.create(field_val)
        if field_val['create_method'] != "together":
            mapper_field_obj.write(
                {'create_method': field_val['create_method']})
        return mapper_field_obj

    def create_mapper(self, mapper_vals, fields_vals):
        """mapper_vals is a dict and fields_vals is a list of dict"""

        exist_mapper = self.search_mapper(mapper_vals['ref_code'])
        if exist_mapper:
            return exist_mapper
        # OBJECTS AND DATA NEEDED
        mapper_obj = self.env['webservice.mapper']
        model_obj = self.env['ir.model']
        dependence_refs = mapper_vals.get('dep_field_ids', '').split('/')
        del mapper_vals['dep_field_ids']
        model_id = model_obj.search([
            ('model', '=', mapper_vals['odoo_model_name'])])
        if not model_id:
            raise UserError(_('model %s not found')
                            % mapper_vals['odoo_model_name'])

        # CREATE MAPPER
        mapper_vals['odoo_model'] = model_id.id
        mapper_vals['active'] = eval(mapper_vals['active'])
        mapper_vals['update'] = eval(mapper_vals['update'])
        mapper_id = mapper_obj.create(mapper_vals)
        # CREATE FIELDS
        for field_val in fields_vals:
            mapper_id.mapper_fields_ids += self.create_field(
                mapper_id.odoo_model_name, field_val
            )
        # ASSIGN DEPENDENCES
        for dependence_ref in dependence_refs:
            dep_mapper = self.search_mapper(dependence_ref)
            if not dep_mapper:
                continue
            dep_field = dep_mapper.mapper_fields_ids.filtered(
                lambda f: not f.dependence_id and
                f.dependence_ref_code == mapper_id.ref_code
            )
            if dep_field:
                dep_field[0].write({'dependence_id': mapper_id.id})

    def import_csv_data(self, data):
        """ assuming there are minimun 3 rows in the csv."""
        data = base64.b64decode(data).decode('utf-8')
        file_input = StringIO(data)
        file_input.seek(0)
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise Warning(_("Not a valid file!"))
        mapper_vals = dict(zip(reader_info[0], reader_info[1]))
        fields_keys = reader_info[2]
        field_vals = []
        del reader_info[:3]
        for i in range(len(reader_info)):
            # Don't read rows that start with ( , ' ' or are empty
            if not (reader_info[i][0] == '' or reader_info[i][0][0] == '('
                    or reader_info[i][0][0] == ' '):
                field = reader_info[i]
                field_vals.append(dict(zip(fields_keys, field)))
        self.create_mapper(mapper_vals, field_vals)

    def action_import(self):
        """Load Inventory data from the CSV file."""
        if not self.attachment_ids:
            raise Warning(_("You need to select a file!"))
        for file_data in self.attachment_ids:
            self.import_csv_data(file_data.datas)
            file_data.unlink()
        return {'type': 'ir.actions.act_window_close'}
