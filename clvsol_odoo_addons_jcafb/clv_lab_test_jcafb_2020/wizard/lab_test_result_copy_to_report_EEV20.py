# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestResultCopyToReportEEV20(models.TransientModel):
    _description = 'Lab Test Result Copy to Report (EEV20)'
    _name = 'clv.lab_test.result.copy_to_report_eev20'

    def _get_default(self, lab_test_type_id_code, criterion_code):
        active_id = self.env['clv.lab_test.result'].browse(self._context.get('active_id'))
        if active_id.lab_test_type_id.code == lab_test_type_id_code:
            result = active_id.criterion_ids.search([
                ('lab_test_result_id', '=', active_id.id),
                ('code', '=', criterion_code),
            ]).result
        else:
            result = False
        return result

    def _set_result(self, lab_test_type_id_code, criterion_code, result):
        active_id = self.env['clv.lab_test.result'].browse(self._context.get('active_id'))
        if active_id.lab_test_type_id.code == lab_test_type_id_code:
            criterion_reg = active_id.criterion_ids.search([
                ('lab_test_result_id', '=', active_id.id),
                ('code', '=', criterion_code),
            ])
            criterion_reg.result = result

    def _copy_result(self, lab_test_type_id_code, criterion_code, result):
        active_id = self.env['clv.lab_test.result'].browse(self._context.get('active_id')).lab_test_report_id
        if active_id.lab_test_type_id.code == lab_test_type_id_code:
            criterion_reg = active_id.criterion_ids.search([
                ('lab_test_report_id', '=', active_id.id),
                ('code', '=', criterion_code),
            ])
            criterion_reg.result = result

    def _default_result_id(self):
        return self._context.get('active_id')
    result_id = fields.Many2one(
        comodel_name='clv.lab_test.result',
        string='Result',
        readonly=True,
        default=_default_result_id
    )

    def _default_lab_test_type_id(self):
        return self.env['clv.lab_test.result'].browse(self._context.get('active_id')).lab_test_type_id
    lab_test_type_id = fields.Many2one(
        comodel_name='clv.lab_test.type',
        string='Lab Test Type',
        readonly=True,
        default=_default_lab_test_type_id
    )

    def _default_lab_test_request_id(self):
        return self.env['clv.lab_test.result'].browse(self._context.get('active_id')).lab_test_request_id
    lab_test_request_id = fields.Many2one(
        comodel_name='clv.lab_test.request',
        string='Lab Test Request',
        readonly=True,
        default=_default_lab_test_request_id
    )

    #
    # EEV20
    #

    def _default_EEV20_resultado(self):
        return self._get_default('EEV20', 'EEV20-01-03')
    EEV20_resultado = fields.Selection([
        ('POSITIVO', 'POSITIVO'),
        ('NEGATIVO', 'NEGATIVO'),
        ('Não realizado', 'Não realizado'),
    ], 'Resultado', readonly=False, default=_default_EEV20_resultado)

    def _write_EEV20_resultado(self):
        self._set_result('EEV20', 'EEV20-01-03', self.EEV20_resultado)
        self._copy_result('EEV20', 'EEV20-01-03', self.EEV20_resultado)

    def _default_EEV20_metodo_utilizado(self):
        return self._get_default('EEV20', 'EEV20-01-05')
    EEV20_metodo_utilizado = fields.Selection([
        ('Swab anal', 'Swab anal'),
        ('Outro', 'Outro'),
    ], 'Método utilizado', readonly=False, default=_default_EEV20_metodo_utilizado)

    def _write_EEV20_metodo_utilizado(self):
        self._set_result('EEV20', 'EEV20-01-05', self.EEV20_metodo_utilizado)
        self._copy_result('EEV20', 'EEV20-01-05', self.EEV20_metodo_utilizado)

    def _default_EEV20_obs(self):
        return self._get_default('EEV20', 'EEV20-01-06')
    EEV20_obs = fields.Char(
        'Observações', readonly=False, default=_default_EEV20_obs
    )

    def _write_EEV20_obs(self):
        self._set_result('EEV20', 'EEV20-01-06', self.EEV20_obs)
        self._copy_result('EEV20', 'EEV20-01-06', self.EEV20_obs)

    def do_result_copy_to_report_EEV20(self):

        self._write_EEV20_resultado()
        self._write_EEV20_metodo_utilizado()
        self._write_EEV20_obs()

        result = self.env['clv.lab_test.result'].browse(self._context.get('active_id'))
        report = self.env['clv.lab_test.report'].search([
            ('id', '=', result.lab_test_report_id.id),
        ])

        if report.id is not False:

            report.approved = result.approved
            report.employee_id = result.employee_id
            report.date_approved = result.date_approved
            report.state = 'approved'

        return True

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
    def do_result_copy_to_report(self):
        self.ensure_one()

        result = self.env['clv.lab_test.result'].browse(self._context.get('active_id'))

        _logger.info(u'%s %s', '>>>>>', result.code)

        return True
