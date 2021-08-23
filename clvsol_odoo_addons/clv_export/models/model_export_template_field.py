# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ModelExportTemplateField(models.Model):
    _description = 'Model Export Template Field'
    _name = "clv.model_export.template.field"
    _order = "sequence"

    name = fields.Char(string='Alias', index=False, required=False)

    model_export_template_id = fields.Many2one(
        comodel_name='clv.model_export.template',
        string='Model Export Template',
        ondelete='cascade'
    )

    model_id = fields.Many2one(
        string='Model',
        related='model_export_template_id.model_id',
        store=False
    )

    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        ondelete='restrict',
        domain="[('model_id','=',model_id)]"
    )
    field_name = fields.Char(string='Name', related='field_id.name', store=False)
    field_ttype = fields.Selection(string='TType', related='field_id.ttype', store=False)

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    model_export_display = fields.Boolean(string='Display in Export', default=True)


class ModelExportTemplate(models.Model):
    _inherit = 'clv.model_export.template'

    model_export_template_field_ids = fields.One2many(
        comodel_name='clv.model_export.template.field',
        inverse_name='model_export_template_id',
        string='Model Export Template Fields'
    )

    count_model_export_template_fields = fields.Integer(
        string='Model Export Template Fields (count)',
        compute='_compute_count_model_export_template_fields',
        store=True
    )

    @api.depends('model_export_template_field_ids')
    def _compute_count_model_export_template_fields(self):
        for r in self:
            r.count_model_export_template_fields = len(r.model_export_template_field_ids)
