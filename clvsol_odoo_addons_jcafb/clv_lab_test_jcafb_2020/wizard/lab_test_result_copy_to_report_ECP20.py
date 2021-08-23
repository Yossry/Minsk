# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestResultCopyToReportECP20(models.TransientModel):
    _description = 'Lab Test Result Copy to Report (ECP20)'
    _name = 'clv.lab_test.result.copy_to_report_ecp20'

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
    # ECP20
    #

    def _default_ECP20_metodos_utilizados(self):
        return self._get_default('ECP20', 'ECP20-05-03')
    # ECP20_metodos_utilizados = fields.Selection([
    #     ('Ritchie', 'Ritchie'),
    #     ('Hoffmann', 'Hoffmann'),
    #     ('Willis', 'Willis'),
    #     ('Ritchie, Hoffmann', 'Ritchie, Hoffmann'),
    #     ('Ritchie, Hoffmann, Willis', 'Ritchie, Hoffmann, Willis'),
    # ], 'Metodologia(s) Empregada(s)', readonly=False, default=_default_ECP20_metodos_utilizados)
    ECP20_metodos_utilizados = fields.Char(
        string='Metodologia(s) Empregada(s)',
        default=_default_ECP20_metodos_utilizados
    )

    def _write_ECP20_metodos_utilizados(self):
        self._set_result('ECP20', 'ECP20-05-03', self.ECP20_metodos_utilizados)
        self._copy_result('ECP20', 'ECP20-05-03', self.ECP20_metodos_utilizados)

    def _default_ECP20_resultado(self):
        return self._get_default('ECP20', 'ECP20-05-04')
    ECP20_resultado = fields.Selection([
        ('POSITIVO', 'POSITIVO'),
        ('NEGATIVO', 'NEGATIVO'),
        ('Não realizado', 'Não realizado'),
    ], 'Resultado', readonly=False, default=_default_ECP20_resultado)

    def _write_ECP20_resultado(self):
        self._set_result('ECP20', 'ECP20-05-04', self.ECP20_resultado)
        self._copy_result('ECP20', 'ECP20-05-04', self.ECP20_resultado)

    def _default_ECP20_parasitas(self):
        return self._get_default('ECP20', 'ECP20-05-05')
    ECP20_parasitas = fields.Char(
        'Parasitas:', readonly=False, default=_default_ECP20_parasitas
    )

    def _write_ECP20_parasitas(self):
        self._set_result('ECP20', 'ECP20-05-05', self.ECP20_lab_test_parasite_names)
        self._copy_result('ECP20', 'ECP20-05-05', self.ECP20_lab_test_parasite_names)

    def _default_ECP20_lab_test_parasite_ids(self):
        LabTestParasite = self.env['clv.lab_test.parasite']
        parasite_ids = []
        if self._get_default('ECP20', 'ECP20-05-05') is not False:
            parasitas = self._get_default('ECP20', 'ECP20-05-05').split(', ')
            for parasita in parasitas:
                parasite = LabTestParasite.search([
                    ('name', '=', parasita),
                ])
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
        return parasite_ids
    ECP20_lab_test_parasite_ids = fields.Many2many(
        comodel_name='clv.lab_test.parasite',
        relation='clv_lab_test_parasite_lab_test_result_copy_to_report_ecp20_rel',
        string='Lab Test Parasites',
        default=_default_ECP20_lab_test_parasite_ids
    )

    ECP20_lab_test_parasite_names = fields.Char(
        string='Parasitas',
        compute='_compute_ECP20_lab_test_parasite_names',
        store=True
    )
    ECP20_lab_test_parasite_names_suport = fields.Char(
        string='Parasite Names Suport',
        compute='_compute_ECP20_lab_test_parasite_names_suport',
        store=False
    )

    @api.depends('ECP20_lab_test_parasite_ids')
    def _compute_ECP20_lab_test_parasite_names(self):
        for r in self:
            r.ECP20_lab_test_parasite_names = r.ECP20_lab_test_parasite_names_suport

    @api.multi
    def _compute_ECP20_lab_test_parasite_names_suport(self):
        for r in self:
            ECP20_lab_test_parasite_names = False
            for parasite in r.ECP20_lab_test_parasite_ids:
                if ECP20_lab_test_parasite_names is False:
                    ECP20_lab_test_parasite_names = parasite.name
                else:
                    ECP20_lab_test_parasite_names = ECP20_lab_test_parasite_names + ', ' + parasite.name
            r.ECP20_lab_test_parasite_names_suport = ECP20_lab_test_parasite_names

    def _default_ECP20_obs(self):
        return self._get_default('ECP20', 'ECP20-05-06')
    ECP20_obs = fields.Text(
        'Observações', readonly=False, default=_default_ECP20_obs
    )

    def _write_ECP20_obs(self):
        self._set_result('ECP20', 'ECP20-05-06', self.ECP20_obs)
        self._copy_result('ECP20', 'ECP20-05-06', self.ECP20_obs)

    def do_result_copy_to_report_ECP20(self):

        self._write_ECP20_metodos_utilizados()
        self._write_ECP20_resultado()
        self._write_ECP20_parasitas()
        self._write_ECP20_obs()

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
