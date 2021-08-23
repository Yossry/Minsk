# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestResultEditEAN20(models.TransientModel):
    _description = 'Lab Test Result Edit (EAN20)'
    _name = 'clv.lab_test.result.edit_ean20'

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
    # EAN20
    #

    def _default_EAN20_peso(self):
        return self._get_default('EAN20', 'EAN20-01-01')
    EAN20_peso = fields.Char(
        'Peso', readonly=False, default=_default_EAN20_peso
    )

    def _write_EAN20_peso(self):
        self._set_result('EAN20', 'EAN20-01-01', self.EAN20_peso)

    def _default_EAN20_peso_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAN20', 'EAN20-01-02')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAN20_peso_resp = fields.Many2one(
        'hr.employee',
        string='Responsável pela medida do Peso',
        readonly=False,
        default=_default_EAN20_peso_resp
    )

    def _write_EAN20_peso_resp(self):
        if self.EAN20_peso_resp.name is not False:
            self._set_result(
                'EAN20', 'EAN20-01-02', self.EAN20_peso_resp.name + ' [' + self.EAN20_peso_resp.code + ']'
            )
        else:
            self._set_result('EAN20', 'EAN20-01-02', False)

    def _default_EAN20_altura(self):
        return self._get_default('EAN20', 'EAN20-01-03')
    EAN20_altura = fields.Char(
        'Altura', readonly=False, default=_default_EAN20_altura
    )

    def _write_EAN20_altura(self):
        self._set_result('EAN20', 'EAN20-01-03', self.EAN20_altura)

    def _default_EAN20_altura_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAN20', 'EAN20-01-04')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAN20_altura_resp = fields.Many2one(
        'hr.employee',
        string='Responsável pela medida da Altura',
        readonly=False,
        default=_default_EAN20_altura_resp
    )

    def _write_EAN20_altura_resp(self):
        if self.EAN20_altura_resp.name is not False:
            self._set_result(
                'EAN20', 'EAN20-01-04', self.EAN20_altura_resp.name + ' [' + self.EAN20_altura_resp.code + ']'
            )
        else:
            self._set_result('EAN20', 'EAN20-01-04', False)

    def _default_EAN20_hemoglobina_coleta_horario(self):
        return self._get_default('EAN20', 'EAN20-02-01')
    EAN20_hemoglobina_coleta_horario = fields.Datetime(
        'Horário da coleta', readonly=False, default=_default_EAN20_hemoglobina_coleta_horario
    )

    def _write_EAN20_hemoglobina_coleta_horario(self):
        self._set_result('EAN20', 'EAN20-02-01', self.EAN20_hemoglobina_coleta_horario)

    def _default_EAN20_hemoglobina_coleta_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAN20', 'EAN20-02-02')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAN20_hemoglobina_coleta_resp = fields.Many2one(
        'hr.employee',
        string='Responsável pela coleta',
        readonly=False,
        default=_default_EAN20_hemoglobina_coleta_resp
    )

    def _write_EAN20_hemoglobina_coleta_resp(self):
        if self.EAN20_hemoglobina_coleta_resp.name is not False:
            self._set_result(
                'EAN20', 'EAN20-02-02',
                self.EAN20_hemoglobina_coleta_resp.name + ' [' + self.EAN20_hemoglobina_coleta_resp.code + ']'
            )
        else:
            self._set_result('EAN20', 'EAN20-02-02', False)

    def _default_EAN20_hemoglobina_valor(self):
        return self._get_default('EAN20', 'EAN20-02-03')
    EAN20_hemoglobina_valor = fields.Char(
        'Valor da Hemoglobina', readonly=False, default=_default_EAN20_hemoglobina_valor
    )

    def _write_EAN20_hemoglobina_valor(self):
        self._set_result('EAN20', 'EAN20-02-03', self.EAN20_hemoglobina_valor)

    def _default_EAN20_hemoglobina_valor_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAN20', 'EAN20-02-04')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAN20_hemoglobina_valor_resp = fields.Many2one(
        'hr.employee',
        string='Responsável pela dosagem',
        readonly=False,
        default=_default_EAN20_hemoglobina_valor_resp
    )

    def _write_EAN20_hemoglobina_valor_resp(self):
        _logger.info(u'%s %s', '>>>>>>>>>>', self.EAN20_hemoglobina_valor_resp.name)
        if self.EAN20_hemoglobina_valor_resp.name is not False:
            self._set_result(
                'EAN20', 'EAN20-02-04',
                self.EAN20_hemoglobina_valor_resp.name + ' [' + self.EAN20_hemoglobina_valor_resp.code + ']'
            )
        else:
            self._set_result('EAN20', 'EAN20-02-04', False)

    def _default_EAN20_hemoglobina_interpretacao(self):
        return self._get_default('EAN20', 'EAN20-02-05')
    EAN20_hemoglobina_interpretacao = fields.Selection([
        ('a) Normal', 'a) Normal'),
        ('b) Abaixo do normal (anemia)', 'b) Abaixo do normal (anemia)'),
        ('c) Acima do normal', 'c) Acima do normal'),
    ], 'Interpretação do Resultado de Hemoglobina', readonly=False, default=_default_EAN20_hemoglobina_interpretacao)

    def _write_EAN20_hemoglobina_interpretacao(self):
        self._set_result('EAN20', 'EAN20-02-05', self.EAN20_hemoglobina_interpretacao)

    def _default_EAN20_obs(self):
        return self._get_default('EAN20', 'EAN20-02-06')
    EAN20_obs = fields.Char(
        'Observações', readonly=False, default=_default_EAN20_obs
    )

    def _write_EAN20_obs(self):
        self._set_result('EAN20', 'EAN20-02-06', self.EAN20_obs)

    def do_result_updt_EAN20(self):

        self._write_EAN20_peso()
        self._write_EAN20_peso_resp()
        self._write_EAN20_altura()
        self._write_EAN20_altura_resp()
        self._write_EAN20_hemoglobina_coleta_horario()
        self._write_EAN20_hemoglobina_coleta_resp()
        self._write_EAN20_hemoglobina_valor()
        self._write_EAN20_hemoglobina_valor_resp()
        self._write_EAN20_hemoglobina_interpretacao()
        self._write_EAN20_obs()

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
    def do_result_updt(self):
        self.ensure_one()

        result = self.env['clv.lab_test.result'].browse(self._context.get('active_id'))

        _logger.info(u'%s %s', '>>>>>', result.code)

        return True
