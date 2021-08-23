# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestResultEditEAA20(models.TransientModel):
    _description = 'Lab Test Result Edit (EAA20)'
    _name = 'clv.lab_test.result.edit_eaa20'

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
    # EAA20
    #

    def _default_EAA20_morador(self):
        person_model = self.env['clv.person']
        code = self._get_default('EAA20', 'EAA20-01-02')
        if code is not False:
            person_search = person_model.search([
                ('code', '=', code),
            ])
            return person_search
        else:
            return False
    EAA20_morador = fields.Many2one(
        'clv.person',
        string='Morador',
        readonly=False,
        default=_default_EAA20_morador
    )

    def _write_EAA20_morador(self):

        if self.EAA20_morador.name is not False:
            self._set_result(
                'EAA20', 'EAA20-01-01', self.EAA20_morador.name
            )
        else:
            self._set_result('EAA20', 'EAA20-01-01', False)

        if self.EAA20_morador.code is not False:
            self._set_result(
                'EAA20', 'EAA20-01-02', self.EAA20_morador.code
            )
        else:
            self._set_result('EAA20', 'EAA20-01-02', False)

    def _default_EAA20_local_coleta(self):
        return self._get_default('EAA20', 'EAA20-02-01')
    EAA20_local_coleta = fields.Char(
        'Local da Coleta', readonly=False, default=_default_EAA20_local_coleta
    )

    def _write_EAA20_local_coleta(self):
        self._set_result('EAA20', 'EAA20-02-01', self.EAA20_local_coleta)

    def _default_EAA20_ponto_coleta(self):
        return self._get_default('EAA20', 'EAA20-02-02')
    EAA20_ponto_coleta = fields.Char(
        'Ponto da Coleta', readonly=False, default=_default_EAA20_ponto_coleta
    )

    def _write_EAA20_ponto_coleta(self):
        self._set_result('EAA20', 'EAA20-02-02', self.EAA20_ponto_coleta)

    def _default_EAA20_data_coleta(self):
        return self._get_default('EAA20', 'EAA20-02-03')
    EAA20_data_coleta = fields.Datetime(
        'Data da coleta', readonly=False, default=_default_EAA20_data_coleta
    )

    def _write_EAA20_data_coleta(self):
        self._set_result('EAA20', 'EAA20-02-03', self.EAA20_data_coleta)

    def _default_EAA20_coleta_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAA20', 'EAA20-02-04')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAA20_coleta_resp = fields.Many2one(
        'hr.employee',
        string='Responsável pela coleta',
        readonly=False,
        default=_default_EAA20_coleta_resp
    )

    def _write_EAA20_coleta_resp(self):
        if self.EAA20_coleta_resp.name is not False:
            self._set_result(
                'EAA20', 'EAA20-02-04',
                self.EAA20_coleta_resp.name + ' [' + self.EAA20_coleta_resp.code + ']'
            )
        else:
            self._set_result('EAA20', 'EAA20-02-04', False)

    def _default_EAA20_cloro_livre_valor(self):
        return self._get_default('EAA20', 'EAA20-03-01')
    EAA20_cloro_livre_valor = fields.Char(
        'Cloro Livre', readonly=False, default=_default_EAA20_cloro_livre_valor
    )

    def _write_EAA20_cloro_livre_valor(self):
        self._set_result('EAA20', 'EAA20-03-01', self.EAA20_cloro_livre_valor)

    def _default_EAA20_data_cloro_livre(self):
        return self._get_default('EAA20', 'EAA20-03-02')
    EAA20_data_cloro_livre = fields.Datetime(
        'Data (Cloro Livre)', readonly=False, default=_default_EAA20_data_cloro_livre
    )

    def _write_EAA20_data_cloro_livre(self):
        self._set_result('EAA20', 'EAA20-03-02', self.EAA20_data_cloro_livre)

    def _default_EAA20_cloro_livre_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAA20', 'EAA20-03-03')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAA20_cloro_livre_resp = fields.Many2one(
        'hr.employee',
        string='Responsável (Cloro Livre)',
        readonly=False,
        default=_default_EAA20_cloro_livre_resp
    )

    def _write_EAA20_cloro_livre_resp(self):
        if self.EAA20_cloro_livre_resp.name is not False:
            self._set_result(
                'EAA20', 'EAA20-03-03',
                self.EAA20_cloro_livre_resp.name + ' [' + self.EAA20_cloro_livre_resp.code + ']'
            )
        else:
            self._set_result('EAA20', 'EAA20-03-03', False)

    def _default_EAA20_ph_valor(self):
        return self._get_default('EAA20', 'EAA20-03-04')
    EAA20_ph_valor = fields.Char(
        'pH', readonly=False, default=_default_EAA20_ph_valor
    )

    def _write_EAA20_ph_valor(self):
        self._set_result('EAA20', 'EAA20-03-04', self.EAA20_ph_valor)

    def _default_EAA20_data_ph(self):
        return self._get_default('EAA20', 'EAA20-03-05')
    EAA20_data_ph = fields.Datetime(
        'Data (pH)', readonly=False, default=_default_EAA20_data_ph
    )

    def _write_EAA20_data_ph(self):
        self._set_result('EAA20', 'EAA20-03-05', self.EAA20_data_ph)

    def _default_EAA20_ph_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAA20', 'EAA20-03-06')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAA20_ph_resp = fields.Many2one(
        'hr.employee',
        string='Responsável (pH)',
        readonly=False,
        default=_default_EAA20_ph_resp
    )

    def _write_EAA20_ph_resp(self):
        if self.EAA20_ph_resp.name is not False:
            self._set_result(
                'EAA20', 'EAA20-03-06',
                self.EAA20_ph_resp.name + ' [' + self.EAA20_ph_resp.code + ']'
            )
        else:
            self._set_result('EAA20', 'EAA20-03-06', False)

    def _default_EAA20_coliformes_totais_valor(self):
        return self._get_default('EAA20', 'EAA20-04-01')
    EAA20_coliformes_totais_valor = fields.Char(
        'Coliformes totais', readonly=False, default=_default_EAA20_coliformes_totais_valor
    )

    def _write_EAA20_coliformes_totais_valor(self):
        self._set_result('EAA20', 'EAA20-04-01', self.EAA20_coliformes_totais_valor)

    def _default_EAA20_data_coliformes_totais(self):
        return self._get_default('EAA20', 'EAA20-04-02')
    EAA20_data_coliformes_totais = fields.Datetime(
        'Data (Coliformes totais)', readonly=False, default=_default_EAA20_data_coliformes_totais
    )

    def _write_EAA20_data_coliformes_totais(self):
        self._set_result('EAA20', 'EAA20-04-02', self.EAA20_data_coliformes_totais)

    def _default_EAA20_coliformes_totais_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAA20', 'EAA20-04-03')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAA20_coliformes_totais_resp = fields.Many2one(
        'hr.employee',
        string='Responsável (Coliformes totais)',
        readonly=False,
        default=_default_EAA20_coliformes_totais_resp
    )

    def _write_EAA20_coliformes_totais_resp(self):
        if self.EAA20_coliformes_totais_resp.name is not False:
            self._set_result(
                'EAA20', 'EAA20-04-03',
                self.EAA20_coliformes_totais_resp.name + ' [' + self.EAA20_coliformes_totais_resp.code + ']'
            )
        else:
            self._set_result('EAA20', 'EAA20-04-03', False)

    def _default_EAA20_escherichia_coli_valor(self):
        return self._get_default('EAA20', 'EAA20-04-04')
    EAA20_escherichia_coli_valor = fields.Char(
        'Escherichia coli', readonly=False, default=_default_EAA20_escherichia_coli_valor
    )

    def _write_EAA20_escherichia_coli_valor(self):
        self._set_result('EAA20', 'EAA20-04-04', self.EAA20_escherichia_coli_valor)

    def _default_EAA20_data_escherichia_coli(self):
        return self._get_default('EAA20', 'EAA20-04-05')
    EAA20_data_escherichia_coli = fields.Datetime(
        'Data (Escherichia coli)', readonly=False, default=_default_EAA20_data_escherichia_coli
    )

    def _write_EAA20_data_escherichia_coli(self):
        self._set_result('EAA20', 'EAA20-04-05', self.EAA20_data_escherichia_coli)

    def _default_EAA20_escherichia_coli_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EAA20', 'EAA20-04-06')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EAA20_escherichia_coli_resp = fields.Many2one(
        'hr.employee',
        string='Responsável (Escherichia coli)',
        readonly=False,
        default=_default_EAA20_escherichia_coli_resp
    )

    def _write_EAA20_escherichia_coli_resp(self):
        if self.EAA20_escherichia_coli_resp.name is not False:
            self._set_result(
                'EAA20', 'EAA20-04-06',
                self.EAA20_escherichia_coli_resp.name + ' [' + self.EAA20_escherichia_coli_resp.code + ']'
            )
        else:
            self._set_result('EAA20', 'EAA20-04-06', False)

    def _default_EAA20_obs(self):
        return self._get_default('EAA20', 'EAA20-05-01')
    EAA20_obs = fields.Char(
        'Observações', readonly=False, default=_default_EAA20_obs
    )

    def _write_EAA20_obs(self):
        self._set_result('EAA20', 'EAA20-05-01', self.EAA20_obs)

    def do_result_updt_EAA20(self):

        self._write_EAA20_morador()
        self._write_EAA20_local_coleta()
        self._write_EAA20_ponto_coleta()
        self._write_EAA20_data_coleta()
        self._write_EAA20_coleta_resp()
        self._write_EAA20_cloro_livre_valor()
        self._write_EAA20_data_cloro_livre()
        self._write_EAA20_cloro_livre_resp()
        self._write_EAA20_ph_valor()
        self._write_EAA20_data_ph()
        self._write_EAA20_ph_resp()
        self._write_EAA20_coliformes_totais_valor()
        self._write_EAA20_data_coliformes_totais()
        self._write_EAA20_coliformes_totais_resp()
        self._write_EAA20_escherichia_coli_valor()
        self._write_EAA20_data_escherichia_coli()
        self._write_EAA20_escherichia_coli_resp()
        self._write_EAA20_obs()

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
