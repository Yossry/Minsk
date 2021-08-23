# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ModelExportTemplateDuplicate(models.TransientModel):
    _description = 'Model Export Template Duplicate'
    _name = 'clv.model_export.template.duplicate'

    model_export_template_ids = fields.Many2many(
        comodel_name='clv.model_export.template',
        relation='clv_model_export_template_duplicate_rel',
        string='Model Export Templates'
    )

    new_name = fields.Char(
        string='New Model Export Template Name',
        required=True
    )

    new_label = fields.Char(
        string='New Model Export Template Label',
        required=True
    )

    @api.model
    def default_get(self, field_names):

        defaults = super(ModelExportTemplateDuplicate, self).default_get(field_names)

        defaults['model_export_template_ids'] = self.env.context['active_ids']

        ModelExportTemplate = self.env['clv.model_export.template']
        model_export_template_id = self._context.get('active_id')
        model_export_template = ModelExportTemplate.search([
            ('id', '=', model_export_template_id),
        ])
        defaults['new_name'] = model_export_template.name
        defaults['new_label'] = model_export_template.label

        return defaults

    @api.multi
    def _reopen_form(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def do_model_export_template_duplicate(self):
        self.ensure_one()

        ModelExportTemplate = self.env['clv.model_export.template']
        ModelExportTemplateField = self.env['clv.model_export.template.field']

        for model_export_template in self.model_export_template_ids:

            _logger.info(u'%s %s %s', '>>>>>', model_export_template.name, model_export_template.label)
            _logger.info(u'%s %s %s', '>>>>>>>>>>', self.new_name, self.new_label)

            values = {
                'name': self.new_name,
                'label': self.new_label,
                'model_id': model_export_template.model_id.id,
                'export_type': model_export_template.export_type,
            }
            if hasattr(ModelExportTemplate, 'use_document_items'):
                values['use_document_items'] = model_export_template.use_document_items
            if hasattr(ModelExportTemplate, 'use_lab_test_criteria'):
                values['use_lab_test_criteria'] = model_export_template.use_lab_test_criteria
            new_model_export_template = ModelExportTemplate.create(values)

            for model_export_template_field in model_export_template.model_export_template_field_ids:

                _logger.info(u'%s %s', '>>>>>>>>>>>>>>>', model_export_template_field.field_id.name)

                values = {
                    'sequence': model_export_template_field.sequence,
                    'name': model_export_template_field.name,
                    'model_export_template_id': new_model_export_template.id,
                    'model_export_display': model_export_template_field.model_export_display,
                    'field_id': model_export_template_field.field_id.id,
                }
                ModelExportTemplateField.create(values)

            if hasattr(ModelExportTemplate, 'use_document_items'):

                ModelExportTemplateDocumentItem = self.env['clv.model_export.template.document_item']
                model_export_template_document_items = ModelExportTemplateDocumentItem.search([
                    ('model_export_template_id', '=', model_export_template.id),
                ])
                for model_export_template_document_item in model_export_template_document_items:
                    _logger.info(u'%s %s', '>>>>>>>>>>>>>>>',
                                 model_export_template_document_item.document_item_id.name)
                    values = {
                        'sequence': model_export_template_document_item.sequence,
                        'name': model_export_template_document_item.name,
                        'model_export_template_id': new_model_export_template.id,
                        'model_export_display': model_export_template_document_item.model_export_display,
                        'document_item_id': model_export_template_document_item.document_item_id.id,
                    }
                    ModelExportTemplateDocumentItem.create(values)

            if hasattr(ModelExportTemplate, 'use_lab_test_criteria'):

                ModelExportTemplateLabTestCriterion = self.env['clv.model_export.template.lab_test_criterion']
                model_export_template_lab_test_criteria = ModelExportTemplateLabTestCriterion.search([
                    ('model_export_template_id', '=', model_export_template.id),
                ])
                for model_export_template_lab_test_criterion in model_export_template_lab_test_criteria:
                    _logger.info(u'%s %s', '>>>>>>>>>>>>>>>',
                                 model_export_template_lab_test_criterion.lab_test_criterion_id.name)
                    values = {
                        'sequence': model_export_template_lab_test_criterion.sequence,
                        'name': model_export_template_lab_test_criterion.name,
                        'model_export_template_id': new_model_export_template.id,
                        'model_export_display': model_export_template_lab_test_criterion.model_export_display,
                        'lab_test_criterion_id': model_export_template_lab_test_criterion.lab_test_criterion_id.id,
                    }
                    ModelExportTemplateLabTestCriterion.create(values)

        return True
