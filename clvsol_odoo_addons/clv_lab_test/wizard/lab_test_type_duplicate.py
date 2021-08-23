# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestTypeDuplicate(models.TransientModel):
    _description = 'Lab Test Type Duplicate'
    _name = 'clv.lab_test.type.duplicate'

    lab_test_type_ids = fields.Many2many(
        comodel_name='clv.lab_test.type',
        relation='clv_lab_test_type_duplicate_rel',
        string='Lab Test Types'
    )

    new_name = fields.Char(
        string='New Lab Test Type',
        required=True
    )

    new_code = fields.Char(
        string='New Lab Test Type Code',
        required=True
    )

    @api.model
    def default_get(self, field_names):

        defaults = super().default_get(field_names)

        defaults['lab_test_type_ids'] = self.env.context['active_ids']

        LabTestType = self.env['clv.lab_test.type']
        lab_test_type_id = self._context.get('active_id')
        lab_test_type = LabTestType.search([
            ('id', '=', lab_test_type_id),
        ])
        defaults['new_name'] = lab_test_type.name
        defaults['new_code'] = lab_test_type.code

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
    def do_lab_test_type_duplicate(self):
        self.ensure_one()

        LabTestType = self.env['clv.lab_test.type']

        lab_test_type_count = 0
        for lab_test_type in self.lab_test_type_ids:

            lab_test_type_count += 1

            _logger.info(u'%s %s %s', '>>>>>', lab_test_type.code, lab_test_type.name)
            _logger.info(u'%s %s %s', '>>>>>>>>>>', self.new_code, self.new_name)

            values = {
                'name': self.new_name,
                'code': self.new_code,
            }
            new_lab_test_type = LabTestType.create(values)

            criteria = []
            for criterion in lab_test_type.criterion_ids:

                criterion_code = False
                if criterion.code is not False:
                    criterion_code = criterion.code.replace(lab_test_type.code, self.new_code)
                criteria.append((0, 0, {'code': criterion_code,
                                        'name': criterion.name,
                                        'unit_id': criterion.unit_id.id,
                                        'result': criterion.result,
                                        'normal_range': criterion.normal_range,
                                        # 'lab_test_type_id': criterion.lab_test_type_id.id,
                                        'sequence': criterion.sequence,
                                        'result_display': criterion.result_display,
                                        'report_display': criterion.report_display,
                                        }))

            new_lab_test_type.criterion_ids = criteria

            _logger.info(u'%s %s', '>>>>>>>>>>>>>>>', criteria)

        if lab_test_type_count == 1:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Lab Test Types',
                'res_model': 'clv.lab_test.type',
                'res_id': new_lab_test_type.id,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
                'context': {'search_default_name': new_lab_test_type.name},
            }

        else:

            action = {
                'type': 'ir.actions.act_window',
                'name': 'Lab Test Types',
                'res_model': 'clv.lab_test.type',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
            }

        return action
        # return True
