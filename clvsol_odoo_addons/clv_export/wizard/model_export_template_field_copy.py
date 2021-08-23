# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ModelExportTemplateFieldCopy(models.TransientModel):
    _description = 'Model Export Template Field Copy'
    _name = 'clv.model_export.template.field.copy'

    model_export_template_field_ids = fields.Many2many(
        comodel_name='clv.model_export.template.field',
        relation='clv_model_export_template_field_copy_rel',
        string='Model Export Template Fields'
    )

    create_new_model_export_template = fields.Boolean(
        string='Create new Model Export Template',
        default=False)

    model_export_template_id = fields.Many2one(
        comodel_name='clv.model_export.template',
        string='Model Export Template',
        required=False
    )

    new_model_export_template_name = fields.Char(
        string='New Model Export Template Name',
        required=False
    )

    new_model_export_model_id = fields.Many2one(
        comodel_name='ir.model',
        string='New Model Export Template Model',
        required=False,
        # domain="[('model','in',['clv.person','clv.address'])]"
    )

    @api.model
    def default_get(self, field_names):

        defaults = super(ModelExportTemplateFieldCopy, self).default_get(field_names)

        defaults['model_export_template_field_ids'] = self.env.context['active_ids']

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
    def do_model_export_template_field_copy(self):
        self.ensure_one()

        ModelExportTemplate = self.env['clv.model_export.template']
        ModelExportTemplateField = self.env['clv.model_export.template.field']

        actual_model_export_template = False

        if self.create_new_model_export_template:

            if self.new_model_export_template_name is False:
                raise UserError(u'"New Model Export Template Name" can not be null!')
                return self._reopen_form()

            else:

                if self.new_model_export_model_id.id is False:
                    raise UserError(u'"New Model Export Template Model" can not be null!')
                    return self._reopen_form()

                else:

                    actual_model_export_template = ModelExportTemplate.search([
                        ('name', '=', self.new_model_export_template_name),
                    ])
                    _logger.info(u'%s %s %s', '>>>>>>>>>>', 'actual_model_export_template_id:',
                                 actual_model_export_template.id)

                    if actual_model_export_template.id is False:

                        values = {}
                        values['name'] = self.new_model_export_template_name
                        _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                        actual_model_export_template = ModelExportTemplate.create(values)
                        _logger.info(u'%s %s %s', '>>>>>>>>>>', 'actual_model_export_template:',
                                     actual_model_export_template)

        else:

            if self.model_export_template_id.id is False:
                raise UserError(u'"Model Export Template" can not be null!')
                return self._reopen_form()

            else:

                actual_model_export_template = self.model_export_template_id
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'actual_model_export_template:', actual_model_export_template)

        for field_count, model_export_template_field in enumerate(self.model_export_template_field_ids):

            _logger.info(u'%s %s %s', '>>>>>', field_count + 1, model_export_template_field.field_id.name)

            actual_model_export_template_field = ModelExportTemplateField.search([
                ('model_export_template_id', '=', actual_model_export_template.id),
                ('field_id', '=', model_export_template_field.field_id.id),
            ])
            _logger.info(u'%s %s %s', '>>>>>>>>>>',
                         'actual_model_export_template_field', actual_model_export_template_field.id)

            if actual_model_export_template_field.id is False:

                values = {}
                values['model_export_template_id'] = actual_model_export_template.id
                values['field_id'] = model_export_template_field.field_id.id
                _logger.info(u'%s %s %s', '>>>>>>>>>>', 'values:', values)
                new_model_export_template_field = ModelExportTemplateField.create(values)
                _logger.info(u'%s %s', '>>>>>>>>>>', new_model_export_template_field.field_id.name)

        return True
