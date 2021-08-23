# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class ModelExportRefresh(models.TransientModel):
    _description = 'Model Export Refresh'
    _name = 'clv.model_export.refresh'

    def _default_model_export_ids(self):
        return self._context.get('active_ids')
    model_export_ids = fields.Many2many(
        comodel_name='clv.model_export',
        relation='clv_model_export_refresh_rel',
        string='Model Exports',
        default=_default_model_export_ids)

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
    def do_model_export_refresh(self):
        self.ensure_one()

        ModelExport = self.env['clv.model_export']
        ModelExportField = self.env['clv.model_export.field']
        ModelExportDocumentItem = self.env['clv.model_export.document_item']
        ModelExportLabTestCriterion = self.env['clv.model_export.lab_test_criterion']

        for model_export in self.model_export_ids:

            _logger.info(u'%s %s %s %s', '>>>>>',
                         model_export.name, model_export.label, model_export.template_id.name)

            if model_export.template_id is not False:

                for model_export_field in model_export.model_export_field_ids:
                    model_export_field.unlink()

                model_export_field_ids = []
                for model_export_template_field in model_export.template_id.model_export_template_field_ids:
                    values = {
                        'name': model_export_template_field.name,
                        'model_export_id': model_export.id,
                        'model_export_display': model_export_template_field.model_export_display,
                        'field_id': model_export_template_field.field_id.id,
                        'sequence': model_export_template_field.sequence,
                    }
                    new_model_export_field = ModelExportField.create(values)
                    model_export_field_ids += [new_model_export_field.id]
                _logger.info(u'%s %s', '>>>>>>>>>>', model_export_field_ids)

                if hasattr(ModelExport, 'use_document_items'):

                    for model_export_document_item in model_export.model_export_document_item_ids:
                        model_export_document_item.unlink()

                    model_export_document_item_ids = []
                    for model_export_template_document_item in \
                            model_export.template_id.model_export_template_document_item_ids:
                        values = {
                            'name': model_export_template_document_item.name,
                            'model_export_id': model_export.id,
                            'model_export_display': model_export_template_document_item.model_export_display,
                            'document_item_id': model_export_template_document_item.document_item_id.id,
                            'sequence': model_export_template_document_item.sequence,
                        }
                        new_model_export_document_item = ModelExportDocumentItem.create(values)
                        model_export_document_item_ids += [new_model_export_document_item.id]
                    _logger.info(u'%s %s', '>>>>>>>>>>', model_export_document_item_ids)

                if hasattr(ModelExport, 'use_lab_test_criteria'):

                    for model_export_template_lab_test_criterion in model_export.model_export_lab_test_criterion_ids:
                        model_export_template_lab_test_criterion.unlink()

                    model_export_lab_test_criterion_ids = []
                    for model_export_template_lab_test_criterion in \
                            model_export.template_id.model_export_template_lab_test_criterion_ids:
                        values = {
                            'name': model_export_template_lab_test_criterion.name,
                            'model_export_id': model_export.id,
                            'model_export_display': model_export_template_lab_test_criterion.model_export_display,
                            'lab_test_criterion_id': model_export_template_lab_test_criterion.lab_test_criterion_id.id,
                            'sequence': model_export_template_lab_test_criterion.sequence,
                        }
                        new_model_lab_test_criterion = ModelExportLabTestCriterion.create(values)
                        model_export_lab_test_criterion_ids += [new_model_lab_test_criterion.id]
                    _logger.info(u'%s %s', '>>>>>>>>>>', model_export_lab_test_criterion_ids)

        return True
