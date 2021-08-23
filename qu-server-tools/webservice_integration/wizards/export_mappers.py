# Copyright 2019 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ExportMappers(models.TransientModel):
    _name = 'export.webservice.mapper'
    _description = 'Export Webservice Mapper'

    _columns_mapper = [
        'ref_code',
        'dep_field_ids',
        'name',
        'active',
        'odoo_model_name',
        'source_model',
        'search_field',
        'search_domain',
        'sequence',
        'method_calls',
        'update',
        'create_active',
        'hide_create_unique_field'
    ]

    def get_export_mapper_data(self, rec):
        """ Get data to export a mapper"""
        return [
            rec.get_ref_code(),
            rec.format_get_dep_fields(),
            rec.name,
            rec.active,
            rec.odoo_model_name or "",
            rec.source_model or "",
            rec.search_field or "",
            rec.search_domain or "",
            rec.sequence or "",
            rec.method_calls or "",
            rec.update,
            rec.create_active,
            rec.hide_create_unique_field,
        ]

    _columns_fields = [
        'odoo_field',
        'source_field',
        'dependence_ref',
        'unique',
        'sequence',
        'map_values',
        'create_method',
        'search_operator'
    ]

    def get_export_field_data(self, rec):
        """Get data to export mapper field"""
        return [
            rec.odoo_field.name,
            rec.source_field or "",
            rec.dependence_id.get_ref_code() or "",
            rec.unique,
            rec.sequence,
            rec.map_values or "",
            rec.create_method or "",
            rec.search_operator or ""
        ]

    name = fields.Char()
    file_ids = fields.One2many(
        comodel_name='export.webservice.file',
        inverse_name='export_id',
        string='Files')


class ExportFiles(models.TransientModel):
    _name = 'export.webservice.file'
    _description = 'Export Webservice Files'

    file_name = fields.Char()
    file_data = fields.Binary(string='File')
    export_id = fields.Many2one(
        comodel_name='export.webservice.mapper'
    )
