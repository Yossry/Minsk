# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestResultEditEDH20(models.TransientModel):
    _description = 'Lab Test Result Edit (EDH20) (2)'
    _name = 'clv.lab_test.result.edit_edh20_2'

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

    def _default_has_complement(self):
        return self.env['clv.lab_test.result'].browse(self._context.get('active_id')).has_complement
    has_complement = fields.Boolean(
        string='Has Complement',
        readonly=True,
        default=_default_has_complement
    )

    def _default_approved(self):
        return self.env['clv.lab_test.result'].browse(self._context.get('active_id')).approved
    approved = fields.Boolean(
        string='Approved',
        readonly=True,
        default=_default_approved
    )

    #
    # EDH20
    #

    readonly = True

    def _default_EDH20_tempo_jejum(self):
        return self._get_default('EDH20', 'EDH20-01-01')
    EDH20_tempo_jejum = fields.Selection([
        (u'a) Menor que 8 hs',
            u'a) Menor que 8 hs'),
        (u'b) Entre 8 e 12 hs',
            u'b) Entre 8 e 12 hs'),
        (u'c) Maior que 12 hs',
            u'c) Maior que 12 hs'),
        (u'd) N??o sabe',
            u'd) N??o sabe'),
        (u'e) N??o quis responder',
            u'e) N??o quis responder'),
        (u'f) N??o se aplica',
            'f) N??o se aplica'),
    ], 'Tempo de Jejum', readonly=False, default=_default_EDH20_tempo_jejum)

    def _write_EDH20_tempo_jejum(self):
        self._set_result('EDH20', 'EDH20-01-01', self.EDH20_tempo_jejum)

    def _default_EDH20_peso(self):
        return self._get_default('EDH20', 'EDH20-02-01')
    EDH20_peso = fields.Char(
        'Peso', readonly=readonly, default=_default_EDH20_peso
    )

    def _write_EDH20_peso(self):
        self._set_result('EDH20', 'EDH20-02-01', self.EDH20_peso)

    def _default_EDH20_peso_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-02-02')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_peso_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pela medida do Peso',
        readonly=False,
        default=_default_EDH20_peso_resp
    )

    def _write_EDH20_peso_resp(self):
        if self.EDH20_peso_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-02-02', self.EDH20_peso_resp.name + ' [' + self.EDH20_peso_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-02-02', False)

    def _default_EDH20_altura(self):
        return self._get_default('EDH20', 'EDH20-02-03')
    EDH20_altura = fields.Char(
        'Altura', readonly=readonly, default=_default_EDH20_altura
    )

    def _write_EDH20_altura(self):
        self._set_result('EDH20', 'EDH20-02-03', self.EDH20_altura)

    def _default_EDH20_altura_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-02-04')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_altura_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pela medida da Altura',
        readonly=False,
        default=_default_EDH20_altura_resp
    )

    def _write_EDH20_altura_resp(self):
        if self.EDH20_altura_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-02-04', self.EDH20_altura_resp.name + ' [' + self.EDH20_altura_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-02-04', False)

    def _default_EDH20_imc(self):
        return self._get_default('EDH20', 'EDH20-02-05')
    EDH20_imc = fields.Char(
        'IMC', readonly=readonly, default=_default_EDH20_imc
    )

    def _write_EDH20_imc(self):
        self._set_result('EDH20', 'EDH20-02-05', self.EDH20_imc)

    def _default_EDH20_imc_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-02-06')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_imc_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pela medida do IMC',
        readonly=False,
        default=_default_EDH20_imc_resp
    )

    def _write_EDH20_imc_resp(self):
        if self.EDH20_imc_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-02-06', self.EDH20_imc_resp.name + ' [' + self.EDH20_imc_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-02-06', False)

    def _default_EDH20_interpretacao_imc(self):
        return self._get_default('EDH20', 'EDH20-02-07')
    EDH20_interpretacao_imc = fields.Selection([
        (u'a) Baixo peso (Adultos:menor que 18,5; Idosos (M e F): menor que 21,9)',
            u'a) Baixo peso (Adultos:menor que 18,5; Idosos (M e F): menor que 21,9)'),
        (u'b) Peso Normal (Adultos: 18,5 a 24,9; Idosos (M e F): 22,0 a 27,0)',
            u'b) Peso Normal (Adultos: 18,5 a 24,9; Idosos (M e F): 22,0 a 27,0)'),
        (u'c) Sobrepeso (Pr??-obeso) (Adultos: 25,0 a 29,9; Idosos(M): 27,1 a 30,0/Idosos(F): 27,1 a 32,0)',
            u'c) Sobrepeso (Pr??-obeso) (Adultos: 25,0 a 29,9; Idosos(M): 27,1 a 30,0/Idosos(F): 27,1 a 32,0)'),
        (u'd) Obesidade Grau I (Adultos: 30,0 a 34,9; Idosos(M): 30,1,1 a 35,0/Idosos(F): 32,1 a 37,0)',
            u'd) Obesidade Grau I (Adultos: 30,0 a 34,9; Idosos(M): 30,1,1 a 35,0/Idosos(F): 32,1 a 37,0)'),
        (u'e) Obesidade Grau II (Adultos: 35,0 a 39,9; Idosos(M): 35,1 a 39,0/Idosos(F): 37,1 a 41,9)',
            u'e) Obesidade Grau II (Adultos: 35,0 a 39,9; Idosos(M): 35,1 a 39,0/Idosos(F): 37,1 a 41,9)'),
        (u'f) Obesidade Grau III (Adultos:maior ou igual a 40,0; Idosos(M):maior ou igual a 40,0/Idosos(F):maior ou igual a 42,0)',
            'f) Obesidade Grau III (Adultos:maior ou igual a 40,0; Idosos(M):maior ou igual a 40,0/Idosos(F):maior ou igual a 42,0)'),
        (u'g) N??o interpretado (justificar em "Observa????es")',
            u'g) N??o interpretado (justificar em "Observa????es")'),
        (u'h) N??o se aplica',
            u'h) N??o se aplica'),
    ], 'Interpreta????o do valor de IMC', readonly=False, default=_default_EDH20_interpretacao_imc)

    def _write_EDH20_interpretacao_imc(self):
        self._set_result('EDH20', 'EDH20-02-07', self.EDH20_interpretacao_imc)

    def _default_EDH20_interpretacao_imc_obs(self):
        return self._get_default('EDH20', 'EDH20-02-08')
    EDH20_interpretacao_imc_obs = fields.Char(
        'Observa????es (IMC)', readonly=False, default=_default_EDH20_interpretacao_imc_obs
    )

    def _write_EDH20_interpretacao_imc_obs(self):
        self._set_result('EDH20', 'EDH20-02-08', self.EDH20_interpretacao_imc_obs)

    def _default_EDH20_circ_abdominal(self):
        return self._get_default('EDH20', 'EDH20-02-09')
    EDH20_circ_abdominal = fields.Char(
        'Circunfer??ncia abdominal', readonly=readonly, default=_default_EDH20_circ_abdominal
    )

    def _write_EDH20_circ_abdominal(self):
        self._set_result('EDH20', 'EDH20-02-09', self.EDH20_circ_abdominal)

    def _default_EDH20_circ_abdominal_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-02-10')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_circ_abdominal_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pela medida da Circunfer??ncia abdominal',
        readonly=False,
        default=_default_EDH20_circ_abdominal_resp
    )

    def _write_EDH20_circ_abdominal_resp(self):
        if self.EDH20_circ_abdominal_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-02-10',
                self.EDH20_circ_abdominal_resp.name + ' [' + self.EDH20_circ_abdominal_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-02-10', False)

    def _default_EDH20_interpretacao_circ_abdominal(self):
        return self._get_default('EDH20', 'EDH20-02-11')
    EDH20_interpretacao_circ_abdominal = fields.Selection([
        (u'a) Normal (H:menor que 94 cm; M:menor que 80 cm)',
            u'a) Normal (H:menor que 94 cm; M:menor que 80 cm)'),
        (u'b) Risco aumentado (H:maior ou igual a 94 cm; M:maior ou igual a 80 cm)',
            u'b) Risco aumentado (H:maior ou igual a 94 cm; M:maior ou igual a 80 cm)'),
        (u'c) Risco aumentado substancialmente (H:maior ou igual a 102 cm; M:maior ou igual a 88 cm))',
            u'c) Risco aumentado substancialmente (H:maior ou igual a 102 cm; M:maior ou igual a 88 cm))'),
        (u'd) N??o interpretado (justificar em observa????es)',
            u'd) N??o interpretado (justificar em observa????es)'),
        (u'e) N??o se aplica',
            u'e) N??o se aplica'),
    ], 'Interpreta????o do valor de Circunfer??ncia Abdominal',
        readonly=False, default=_default_EDH20_interpretacao_circ_abdominal)

    def _write_EDH20_interpretacao_circ_abdominal(self):
        self._set_result('EDH20', 'EDH20-02-11', self.EDH20_interpretacao_circ_abdominal)

    def _default_EDH20_interpretacao_circ_abdominal_obs(self):
        return self._get_default('EDH20', 'EDH20-02-12')
    EDH20_interpretacao_circ_abdominal_obs = fields.Char(
        'Observa????es (Circ Abdm)', readonly=False, default=_default_EDH20_interpretacao_circ_abdominal_obs
    )

    def _write_EDH20_interpretacao_circ_abdominal_obs(self):
        self._set_result('EDH20', 'EDH20-02-12', self.EDH20_interpretacao_circ_abdominal_obs)

    def _default_EDH20_pa_automatica(self):
        return self._get_default('EDH20', 'EDH20-03-01')
    EDH20_pa_automatica = fields.Char(
        'Press??o arterial autom??tica', readonly=readonly, default=_default_EDH20_pa_automatica
    )

    def _write_EDH20_pa_automatica(self):
        self._set_result('EDH20', 'EDH20-03-01', self.EDH20_pa_automatica)

    def _default_EDH20_pa_automatica_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-03-02')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_pa_automatica_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pela medida da Press??o arterial autom??tica',
        readonly=False,
        default=_default_EDH20_pa_automatica_resp
    )

    def _write_EDH20_pa_automatica_resp(self):
        if self.EDH20_pa_automatica_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-03-02',
                self.EDH20_pa_automatica_resp.name + ' [' + self.EDH20_pa_automatica_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-03-02', False)

    def _default_EDH20_pa_manual(self):
        return self._get_default('EDH20', 'EDH20-03-03')
    EDH20_pa_manual = fields.Char(
        'Press??o arterial manual', readonly=readonly, default=_default_EDH20_pa_manual
    )

    def _write_EDH20_pa_manual(self):
        self._set_result('EDH20', 'EDH20-03-03', self.EDH20_pa_manual)

    def _default_EDH20_pa_manual_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-03-04')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_pa_manual_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pela medida da Press??o arterial manual',
        readonly=False,
        default=_default_EDH20_pa_manual_resp
    )

    def _write_EDH20_pa_manual_resp(self):
        if self.EDH20_pa_manual_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-03-04',
                self.EDH20_pa_manual_resp.name + ' [' + self.EDH20_pa_manual_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-03-04', False)

    def _default_EDH20_pa(self):
        return self._get_default('EDH20', 'EDH20-03-05')
    EDH20_pa = fields.Char(
        'Press??o arterial', readonly=False, default=_default_EDH20_pa
    )

    def _write_EDH20_pa(self):
        self._set_result('EDH20', 'EDH20-03-05', self.EDH20_pa)

    def _default_EDH20_PAS(self):
        return self._get_default('EDH20', 'EDH20-03-06')
    EDH20_PAS = fields.Char(
        'PAS', readonly=readonly, default=_default_EDH20_PAS
    )

    def _write_EDH20_PAS(self):
        self._set_result('EDH20', 'EDH20-03-06', self.EDH20_PAS)

    def _default_EDH20_PAD(self):
        return self._get_default('EDH20', 'EDH20-03-07')
    EDH20_PAD = fields.Char(
        'PAD', readonly=readonly, default=_default_EDH20_PAD
    )

    def _write_EDH20_PAD(self):
        self._set_result('EDH20', 'EDH20-03-07', self.EDH20_PAD)

    def _default_EDH20_interpretacao_pa(self):
        return self._get_default('EDH20', 'EDH20-03-08')
    EDH20_interpretacao_pa = fields.Selection([
        (u'a) Normal (PAS menor ou igual a 120 mmHg e PAD menor ou igual a 80 mmHg)',
            u'a) Normal (PAS menor ou igual a 120 mmHg e PAD menor ou igual a 80 mmHg)'),
        (u'b) Pr??-hipertens??o (PAS:121-139 mmHg e PAD:81-89 mmHg)',
            u'b) Pr??-hipertens??o (PAS:121-139 mmHg e PAD:81-89 mmHg)'),
        (u'c) Hipertens??o est??gio 1 (PAS:140-159 mmHg e PAD:90-99 mmHg)',
            u'c) Hipertens??o est??gio 1 (PAS:140-159 mmHg e PAD:90-99 mmHg)'),
        (u'd) Hipertens??o est??gio 2 (PAS:160-179 mmHg e PAD:100-109 mmHg)',
            u'd) Hipertens??o est??gio 2 (PAS:160-179 mmHg e PAD:100-109 mmHg)'),
        (u'e) Hipertens??o est??gio 3 (PAS:maior ou igual a 180 mmHg e PAD:maior ou igual a 110 mmHg)',
            u'e) Hipertens??o est??gio 3 (PAS:maior ou igual a 180 mmHg e PAD:maior ou igual a 110 mmHg)'),
        (u'f) N??o interpretado (justificar em "Observa????es")',
            u'f) N??o interpretado (justificar em "Observa????es")'),
        (u'g) N??o se aplica',
            u'g) N??o se aplica'),
    ], 'Interpreta????o do valor de Press??o Arterial',
        readonly=False, default=_default_EDH20_interpretacao_pa)

    def _write_EDH20_interpretacao_pa(self):
        self._set_result('EDH20', 'EDH20-03-08', self.EDH20_interpretacao_pa)

    def _default_EDH20_interpretacao_pa_obs(self):
        return self._get_default('EDH20', 'EDH20-03-09')
    EDH20_interpretacao_pa_obs = fields.Char(
        'Observa????es (PA)', readonly=False, default=_default_EDH20_interpretacao_pa_obs
    )

    def _write_EDH20_interpretacao_pa_obs(self):
        self._set_result('EDH20', 'EDH20-03-09', self.EDH20_interpretacao_pa_obs)

    def _default_EDH20_glicemia(self):
        return self._get_default('EDH20', 'EDH20-04-01')
    EDH20_glicemia = fields.Char(
        'Glicemia', readonly=readonly, default=_default_EDH20_glicemia
    )

    def _write_EDH20_glicemia(self):
        self._set_result('EDH20', 'EDH20-04-01', self.EDH20_glicemia)

    def _default_EDH20_glicemia_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-04-02')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_glicemia_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pela medida da Glicemia',
        readonly=False,
        default=_default_EDH20_glicemia_resp
    )

    def _write_EDH20_glicemia_resp(self):
        if self.EDH20_glicemia_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-04-02',
                self.EDH20_glicemia_resp.name + ' [' + self.EDH20_glicemia_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-04-02', False)

    def _default_EDH20_interpretacao_glicemia(self):
        return self._get_default('EDH20', 'EDH20-04-03')
    EDH20_interpretacao_glicemia = fields.Selection([
        (u'a) Normal para jejum de 8-12 hs(menor ou igual a 99 mg/dL)',
            u'a) Normal para jejum de 8-12 hs(menor ou igual a 99 mg/dL)'),
        (u'b) Pr??-diabetes (para jejum de 8-12 hs) = risco aumentado para diabetes (100-125 mg/dL)',
            u'b) Pr??-diabetes (para jejum de 8-12 hs) = risco aumentado para diabetes (100-125 mg/dL)'),
        (u'c) Diabetes - para jejum de 8-12 hs (maior que 126 mg/dL, )',
            u'c) Diabetes - para jejum de 8-12 hs (maior que 126 mg/dL, )'),
        (u'd) Jejum INFERIOR a 8 hs: Normal (at?? 140 mg/dL)',
            u'd) Jejum INFERIOR a 8 hs: Normal (at?? 140 mg/dL)'),
        (u'e) Jejum INFERIOR a 8 hs: Aumentado (maior ou igual a 140 mg/dL)',
            u'e) Jejum INFERIOR a 8 hs: Aumentado (maior ou igual a 140 mg/dL)'),
        (u'f) N??o avaliado (justificar)',
            u'f) N??o avaliado (justificar)'),
        (u'g) N??o se aplica',
            u'g) N??o se aplica'),
    ], 'Interpreta????o do valor de Glicemia',
        readonly=False, default=_default_EDH20_interpretacao_glicemia)

    def _write_EDH20_interpretacao_glicemia(self):
        self._set_result('EDH20', 'EDH20-04-03', self.EDH20_interpretacao_glicemia)

    def _default_EDH20_interpretacao_glicemia_obs(self):
        return self._get_default('EDH20', 'EDH20-04-04')
    EDH20_interpretacao_glicemia_obs = fields.Char(
        'Observa????es (Glicemia)', readonly=False, default=_default_EDH20_interpretacao_glicemia_obs
    )

    def _write_EDH20_interpretacao_glicemia_obs(self):
        self._set_result('EDH20', 'EDH20-04-04', self.EDH20_interpretacao_glicemia_obs)

    def _default_EDH20_colesterol(self):
        return self._get_default('EDH20', 'EDH20-04-05')
    EDH20_colesterol = fields.Char(
        'Colesterol', readonly=readonly, default=_default_EDH20_colesterol
    )

    def _write_EDH20_colesterol(self):
        self._set_result('EDH20', 'EDH20-04-05', self.EDH20_colesterol)

    def _default_EDH20_colesterol_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-04-06')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_colesterol_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pela medida da Colesterol',
        readonly=False,
        default=_default_EDH20_colesterol_resp
    )

    def _write_EDH20_colesterol_resp(self):
        if self.EDH20_colesterol_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-04-06',
                self.EDH20_colesterol_resp.name + ' [' + self.EDH20_colesterol_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-04-06', False)

    def _default_EDH20_interpretacao_colesterol(self):
        return self._get_default('EDH20', 'EDH20-04-07')
    EDH20_interpretacao_colesterol = fields.Selection([
        (u'a) Desej??vel:Acima de 20 anos:menor que 190 mg/dL;2-19 anos:menor que 170 mg/dL',
            u'a) Desej??vel:Acima de 20 anos:menor que 190 mg/dL;2-19 anos:menor que 170 mg/dL'),
        (u'b) Alto: Acima de 20 anos:maior ou igual a 190 mg/dL;2-19 anos:maior ou igual a 170 mg/dL',
            u'b) Alto: Acima de 20 anos:maior ou igual a 190 mg/dL;2-19 anos:maior ou igual a 170 mg/dL'),
        (u'c) N??o interpretado (justificar em "Observa????es")',
            u'c) N??o interpretado (justificar em "Observa????es")'),
        (u'd) N??o se aplica',
            u'd) N??o se aplica'),
    ], 'Interpreta????o do valor de Colesterol',
        readonly=False, default=_default_EDH20_interpretacao_colesterol)

    def _write_EDH20_interpretacao_colesterol(self):
        self._set_result('EDH20', 'EDH20-04-07', self.EDH20_interpretacao_colesterol)

    def _default_EDH20_interpretacao_colesterol_obs(self):
        return self._get_default('EDH20', 'EDH20-04-08')
    EDH20_interpretacao_colesterol_obs = fields.Char(
        'Observa????es (Colesterol)', readonly=False, default=_default_EDH20_interpretacao_colesterol_obs
    )

    def _write_EDH20_interpretacao_colesterol_obs(self):
        self._set_result('EDH20', 'EDH20-04-08', self.EDH20_interpretacao_colesterol_obs)

    def _default_EDH20_colesterol_copia(self):
        return self._get_default('EDH20', 'EDH20-04-09')
    EDH20_colesterol_copia = fields.Char(
        'Colesterol (c??pia)', readonly=readonly, default=_default_EDH20_colesterol_copia
    )

    def _write_EDH20_colesterol_copia(self):
        self._set_result('EDH20', 'EDH20-04-09', self.EDH20_colesterol_copia)

    def _default_EDH20_obs(self):
        return self._get_default('EDH20', 'EDH20-05-01')
    EDH20_obs = fields.Char(
        'Observa????es', readonly=readonly, default=_default_EDH20_obs
    )

    def _write_EDH20_obs(self):
        self._set_result('EDH20', 'EDH20-05-01', self.EDH20_obs)

    def _default_EDH20_colesterol_total(self):
        return self._get_default('EDH20', 'EDH20-06-01')
    EDH20_colesterol_total = fields.Char(
        'Colesterol total', readonly=readonly, default=_default_EDH20_colesterol_total
    )

    def _write_EDH20_colesterol_total(self):
        self._set_result('EDH20', 'EDH20-06-01', self.EDH20_colesterol_total)

    def _default_EDH20_interpretacao_colesterol_total(self):
        return self._get_default('EDH20', 'EDH20-06-02')
    EDH20_interpretacao_colesterol_total = fields.Selection([
        (u'a) Desej??vel:Acima de 20 anos:menor que 190 mg/dL;2-19 anos:menor que 170 mg/dL',
            u'a) Desej??vel:Acima de 20 anos:menor que 190 mg/dL;2-19 anos:menor que 170 mg/dL'),
        (u'b) Alto: Acima de 20 anos:maior ou igual a 190 mg/dL;2-19 anos:maior ou igual a 170 mg/dL',
            u'b) Alto: Acima de 20 anos:maior ou igual a 190 mg/dL;2-19 anos:maior ou igual a 170 mg/dL'),
        (u'c) N??o interpretado (justificar em "Observa????es")',
            u'c) N??o interpretado (justificar em "Observa????es")'),
        (u'd) N??o se aplica',
            u'd) N??o se aplica'),
    ], 'Interpreta????o do valor de Colesterol total',
        readonly=False, default=_default_EDH20_interpretacao_colesterol_total)

    def _write_EDH20_interpretacao_colesterol_total(self):
        self._set_result('EDH20', 'EDH20-06-02', self.EDH20_interpretacao_colesterol_total)

    def _default_EDH20_interpretacao_colesterol_total_obs(self):
        return self._get_default('EDH20', 'EDH20-06-03')
    EDH20_interpretacao_colesterol_total_obs = fields.Char(
        'Observa????es (Colesterol total)', readonly=False, default=_default_EDH20_interpretacao_colesterol_total_obs
    )

    def _write_EDH20_interpretacao_colesterol_total_obs(self):
        self._set_result('EDH20', 'EDH20-06-03', self.EDH20_interpretacao_colesterol_total_obs)

    def _default_EDH20_hdl_colesterol(self):
        return self._get_default('EDH20', 'EDH20-06-04')
    EDH20_hdl_colesterol = fields.Char(
        'HDL-Colesterol', readonly=readonly, default=_default_EDH20_hdl_colesterol
    )

    def _write_EDH20_hdl_colesterol(self):
        self._set_result('EDH20', 'EDH20-06-04', self.EDH20_hdl_colesterol)

    def _default_EDH20_interpretacao_hdl_colesterol(self):
        return self._get_default('EDH20', 'EDH20-06-05')
    EDH20_interpretacao_hdl_colesterol = fields.Selection([
        (u'a) Desej??vel:Acima de 20 anos: maior que 40 mg/dL;2-19 anos: maior que 45 mg/dL',
            u'a) Desej??vel:Acima de 20 anos: maior que 40 mg/dL;2-19 anos: maior que 45 mg/dL'),
        (u'b) Baixo: Acima de 20 anos: menor ou igual a 40 mg/dL;2-19 anos: menor ou igual a 45 mg/dL',
            u'b) Baixo: Acima de 20 anos: menor ou igual a 40 mg/dL;2-19 anos: menor ou igual a 45 mg/dL'),
        (u'c) Leitura n??o realizada pelo equipamento',
            u'c) Leitura n??o realizada pelo equipamento'),
        (u'd) N??o interpretado (justificar em "Observa????es")',
            u'd) N??o interpretado (justificar em "Observa????es")'),
        (u'e) N??o se aplica',
            u'e) N??o se aplica'),
    ], 'Interpreta????o do valor de HDL-Colesterol',
        readonly=False, default=_default_EDH20_interpretacao_hdl_colesterol)

    def _write_EDH20_interpretacao_hdl_colesterol(self):
        self._set_result('EDH20', 'EDH20-06-05', self.EDH20_interpretacao_hdl_colesterol)

    def _default_EDH20_interpretacao_hdl_colesterol_obs(self):
        return self._get_default('EDH20', 'EDH20-06-06')
    EDH20_interpretacao_hdl_colesterol_obs = fields.Char(
        'Observa????es (HDL-Colesterol)', readonly=False, default=_default_EDH20_interpretacao_hdl_colesterol_obs
    )

    def _write_EDH20_interpretacao_hdl_colesterol_obs(self):
        self._set_result('EDH20', 'EDH20-06-06', self.EDH20_interpretacao_hdl_colesterol_obs)

    def _default_EDH20_ldl_colesterol(self):
        return self._get_default('EDH20', 'EDH20-06-07')
    EDH20_ldl_colesterol = fields.Char(
        'LDL-Colesterol', readonly=readonly, default=_default_EDH20_ldl_colesterol
    )

    def _write_EDH20_ldl_colesterol(self):
        self._set_result('EDH20', 'EDH20-06-07', self.EDH20_ldl_colesterol)

    def _default_EDH20_fracao_nao_hdl(self):
        return self._get_default('EDH20', 'EDH20-06-08')
    EDH20_fracao_nao_hdl = fields.Char(
        'Fra????o n??o HDL', readonly=readonly, default=_default_EDH20_fracao_nao_hdl
    )

    def _write_EDH20_fracao_nao_hdl(self):
        self._set_result('EDH20', 'EDH20-06-08', self.EDH20_fracao_nao_hdl)

    def _default_EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl(self):
        return self._get_default('EDH20', 'EDH20-06-09')
    EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl = fields.Selection([
        (u'a) A interpreta????o dos resultados dever?? considerar a categoria de risco cardiovascular do paciente, e esta deve ser analisada pelo m??dico',
            u'a) A interpreta????o dos resultados dever?? considerar a categoria de risco cardiovascular do paciente, e esta deve ser analisada pelo m??dico'),
        (u'b) Leitura n??o realizada pelo equipamento',
            u'b) Leitura n??o realizada pelo equipamento'),
        (u'c) N??o se aplica',
            u'c) N??o se aplica'),
    ], 'Interpreta????o do valor de LDL-Colesterol e Fra????o n??o HDL',
        readonly=False, default=_default_EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl)

    def _write_EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl(self):
        self._set_result('EDH20', 'EDH20-06-09', self.EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl)

    def _default_EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl_obs(self):
        return self._get_default('EDH20', 'EDH20-06-10')
    EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl_obs = fields.Char(
        'Observa????es (LDL-Colesterol / Fra????o n??o HDL)', readonly=False,
        default=_default_EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl_obs
    )

    def _write_EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl_obs(self):
        self._set_result('EDH20', 'EDH20-06-10', self.EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl_obs)

    def _default_EDH20_triglicerides(self):
        return self._get_default('EDH20', 'EDH20-07-01')
    EDH20_triglicerides = fields.Char(
        'Triglic??rides', readonly=readonly, default=_default_EDH20_triglicerides
    )

    def _write_EDH20_triglicerides(self):
        self._set_result('EDH20', 'EDH20-07-01', self.EDH20_triglicerides)

    def _default_EDH20_interpretacao_triglicerides(self):
        return self._get_default('EDH20', 'EDH20-07-02')
    EDH20_interpretacao_triglicerides = fields.Selection([
        (u'a) Desej??vel:Acima de 20 anos:menor que 150 mg/dL;10-19 anos:menor que 190 mg/dL;0-9 anos:menor que 75 mg/dL',
            u'a) Desej??vel:Acima de 20 anos:menor que 150 mg/dL;10-19 anos:menor que 190 mg/dL;0-9 anos:menor que 75 mg/dL'),
        (u'b) Alto: Acima de 20 anos:maior ou igual a 150 mg/dL;2-19 anos:maior ou igual a 190 mg/dL;0-9 anos:maior ou igual a 75 mg/dL',
            u'b) Alto: Acima de 20 anos:maior ou igual a 150 mg/dL;2-19 anos:maior ou igual a 190 mg/dL;0-9 anos:maior ou igual a 75 mg/dL'),
        (u'c) Leitura n??o realizada pelo equipamento',
            u'c) Leitura n??o realizada pelo equipamento'),
        (u'd) N??o interpretado (justificar em "Observa????es")',
            u'd) N??o interpretado (justificar em "Observa????es")'),
        (u'e) N??o se aplica',
            u'e) N??o se aplica'),
    ], 'Interpreta????o do valor de Triglic??rides',
        readonly=False, default=_default_EDH20_interpretacao_triglicerides)

    def _write_EDH20_interpretacao_triglicerides(self):
        self._set_result('EDH20', 'EDH20-07-02', self.EDH20_interpretacao_triglicerides)

    def _default_EDH20_interpretacao_triglicerides_obs(self):
        return self._get_default('EDH20', 'EDH20-07-03')
    EDH20_interpretacao_triglicerides_obs = fields.Char(
        'Observa????es (Triglic??rides)', readonly=False, default=_default_EDH20_interpretacao_triglicerides_obs
    )

    def _write_EDH20_interpretacao_triglicerides_obs(self):
        self._set_result('EDH20', 'EDH20-07-03', self.EDH20_interpretacao_triglicerides_obs)

    def _default_EDH20_medidas_resp(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('EDH20', 'EDH20-08-01')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    EDH20_medidas_resp = fields.Many2one(
        'hr.employee',
        string='Respons??vel pelas medidas',
        readonly=False,
        default=_default_EDH20_medidas_resp
    )

    def _write_EDH20_medidas_resp(self):
        if self.EDH20_medidas_resp.name is not False:
            self._set_result(
                'EDH20', 'EDH20-08-01', self.EDH20_medidas_resp.name + ' [' + self.EDH20_medidas_resp.code + ']'
            )
        else:
            self._set_result('EDH20', 'EDH20-08-01', False)

    def _default_EDH20_obs_2(self):
        return self._get_default('EDH20', 'EDH20-08-02')
    EDH20_obs_2 = fields.Char(
        'Observa????es (2)', readonly=readonly, default=_default_EDH20_obs_2
    )

    def _write_EDH20_obs_2(self):
        self._set_result('EDH20', 'EDH20-08-02', self.EDH20_obs_2)

    def do_result_updt_EDH20(self):

        self._write_EDH20_tempo_jejum()
        self._write_EDH20_peso()
        self._write_EDH20_peso_resp()
        self._write_EDH20_altura()
        self._write_EDH20_altura_resp()
        self._write_EDH20_imc()
        self._write_EDH20_imc_resp()
        self._write_EDH20_interpretacao_imc()
        self._write_EDH20_interpretacao_imc_obs()
        self._write_EDH20_circ_abdominal()
        self._write_EDH20_circ_abdominal_resp()
        self._write_EDH20_interpretacao_circ_abdominal()
        self._write_EDH20_interpretacao_circ_abdominal_obs()
        self._write_EDH20_pa_automatica()
        self._write_EDH20_pa_automatica_resp()
        self._write_EDH20_pa_manual()
        self._write_EDH20_pa_manual_resp()
        self._write_EDH20_interpretacao_pa()
        self._write_EDH20_pa()
        self._write_EDH20_PAS()
        self._write_EDH20_PAD()
        self._write_EDH20_interpretacao_pa_obs()
        self._write_EDH20_glicemia()
        self._write_EDH20_glicemia_resp()
        self._write_EDH20_interpretacao_glicemia()
        self._write_EDH20_interpretacao_glicemia_obs()
        self._write_EDH20_colesterol()
        self._write_EDH20_colesterol_resp()
        self._write_EDH20_interpretacao_colesterol()
        self._write_EDH20_interpretacao_colesterol_obs()
        self._write_EDH20_colesterol_copia()
        self._write_EDH20_obs()

        self._write_EDH20_colesterol_total()
        self._write_EDH20_interpretacao_colesterol_total()
        self._write_EDH20_interpretacao_colesterol_total_obs()
        self._write_EDH20_hdl_colesterol()
        self._write_EDH20_interpretacao_hdl_colesterol()
        self._write_EDH20_interpretacao_hdl_colesterol_obs()
        self._write_EDH20_ldl_colesterol()
        self._write_EDH20_fracao_nao_hdl()
        self._write_EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl()
        self._write_EDH20_interpretacao_ldl_colesterol_fracao_nao_hdl_obs()
        self._write_EDH20_triglicerides()
        self._write_EDH20_interpretacao_triglicerides()
        self._write_EDH20_interpretacao_triglicerides_obs()
        self._write_EDH20_medidas_resp()
        self._write_EDH20_obs_2()

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
