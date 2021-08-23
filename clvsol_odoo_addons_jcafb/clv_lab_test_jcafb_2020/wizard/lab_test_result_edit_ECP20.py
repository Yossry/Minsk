# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestResultEditECP20(models.TransientModel):
    _description = 'Lab Test Result Edit (ECP20)'
    _name = 'clv.lab_test.result.edit_ecp20'

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
    # ECP20
    #

    def _default_ECP20_metodo_utilizado_1(self):
        return self._get_default('ECP20', 'ECP20-01-01')
    ECP20_metodo_utilizado_1 = fields.Selection([
        ('Ritchie', 'Ritchie'),
        ('Hoffmann', 'Hoffmann'),
        ('Faust', 'Faust'),
        ('Willis', 'Willis'),
    ], 'Metodologia Empregada (1)', readonly=False, default=_default_ECP20_metodo_utilizado_1)

    def _write_ECP20_metodo_utilizado_1(self):
        self._set_result('ECP20', 'ECP20-01-01', self.ECP20_metodo_utilizado_1)

    def _default_ECP20_resultado_1(self):
        return self._get_default('ECP20', 'ECP20-01-02')
    ECP20_resultado_1 = fields.Selection([
        ('POSITIVO', 'POSITIVO'),
        ('NEGATIVO', 'NEGATIVO'),
        ('Não realizado', 'Não realizado'),
    ], 'Resultado (1)', readonly=False, default=_default_ECP20_resultado_1)

    def _write_ECP20_resultado_1(self):
        self._set_result('ECP20', 'ECP20-01-02', self.ECP20_resultado_1)

    def _default_ECP20_examinador_1(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('ECP20', 'ECP20-01-03')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    ECP20_examinador_1 = fields.Many2one(
        'hr.employee',
        string='Examinador (1)',
        readonly=False,
        default=_default_ECP20_examinador_1
    )

    def _write_ECP20_examinador_1(self):
        if self.ECP20_examinador_1.name is not False:
            self._set_result(
                'ECP20', 'ECP20-01-03',
                self.ECP20_examinador_1.name + ' [' + self.ECP20_examinador_1.code + ']'
            )
        else:
            self._set_result('ECP20', 'ECP20-01-03', False)

    def _default_ECP20_parasitas_1(self):
        return self._get_default('ECP20', 'ECP20-01-04')
    ECP20_parasitas_1 = fields.Char(
        'Parasitas (1):', readonly=False, default=_default_ECP20_parasitas_1
    )

    def _write_ECP20_parasitas_1(self):
        self._set_result('ECP20', 'ECP20-01-04', self.ECP20_lab_test_parasite_1_names)

    def _default_ECP20_lab_test_parasite_1_ids(self):
        LabTestParasite = self.env['clv.lab_test.parasite']
        parasite_ids = []
        if self._get_default('ECP20', 'ECP20-01-04') is not False:
            parasitas = self._get_default('ECP20', 'ECP20-01-04').split(', ')
            for parasita in parasitas:
                parasite = LabTestParasite.search([
                    ('name', '=', parasita),
                ])
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
        return parasite_ids
    ECP20_lab_test_parasite_1_ids = fields.Many2many(
        comodel_name='clv.lab_test.parasite',
        relation='clv_lab_test_parasite_1_lab_test_result_edit_ecp20_rel',
        string='Lab Test Parasites (1)',
        default=_default_ECP20_lab_test_parasite_1_ids
    )

    ECP20_lab_test_parasite_1_names = fields.Char(
        string='Parasitas (1)',
        compute='_compute_ECP20_lab_test_parasite_1_names',
        store=True
    )
    ECP20_lab_test_parasite_1_names_suport = fields.Char(
        string='Parasite Names Suport (1)',
        compute='_compute_ECP20_lab_test_parasite_1_names_suport',
        store=False
    )

    @api.depends('ECP20_lab_test_parasite_1_ids')
    def _compute_ECP20_lab_test_parasite_1_names(self):
        for r in self:
            r.ECP20_lab_test_parasite_1_names = r.ECP20_lab_test_parasite_1_names_suport

    @api.multi
    def _compute_ECP20_lab_test_parasite_1_names_suport(self):
        for r in self:
            ECP20_lab_test_parasite_1_names = False
            for parasite in r.ECP20_lab_test_parasite_1_ids:
                if ECP20_lab_test_parasite_1_names is False:
                    ECP20_lab_test_parasite_1_names = parasite.name
                else:
                    ECP20_lab_test_parasite_1_names = ECP20_lab_test_parasite_1_names + ', ' + parasite.name
            r.ECP20_lab_test_parasite_1_names_suport = ECP20_lab_test_parasite_1_names

    # Exame Coproparasitológico (2)

    def _default_ECP20_metodo_utilizado_2(self):
        return self._get_default('ECP20', 'ECP20-02-01')
    ECP20_metodo_utilizado_2 = fields.Selection([
        ('Ritchie', 'Ritchie'),
        ('Hoffmann', 'Hoffmann'),
        ('Faust', 'Faust'),
        ('Willis', 'Willis'),
    ], 'Metodologia Empregada (2)', readonly=False, default=_default_ECP20_metodo_utilizado_2)

    def _write_ECP20_metodo_utilizado_2(self):
        self._set_result('ECP20', 'ECP20-02-01', self.ECP20_metodo_utilizado_2)

    def _default_ECP20_resultado_2(self):
        return self._get_default('ECP20', 'ECP20-02-02')
    ECP20_resultado_2 = fields.Selection([
        ('POSITIVO', 'POSITIVO'),
        ('NEGATIVO', 'NEGATIVO'),
        ('Não realizado', 'Não realizado'),
    ], 'Resultado (2)', readonly=False, default=_default_ECP20_resultado_2)

    def _write_ECP20_resultado_2(self):
        self._set_result('ECP20', 'ECP20-02-02', self.ECP20_resultado_2)

    def _default_ECP20_examinador_2(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('ECP20', 'ECP20-02-03')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    ECP20_examinador_2 = fields.Many2one(
        'hr.employee',
        string='Examinador (2)',
        readonly=False,
        default=_default_ECP20_examinador_2
    )

    def _write_ECP20_examinador_2(self):
        if self.ECP20_examinador_2.name is not False:
            self._set_result(
                'ECP20', 'ECP20-02-03',
                self.ECP20_examinador_2.name + ' [' + self.ECP20_examinador_2.code + ']'
            )
        else:
            self._set_result('ECP20', 'ECP20-02-03', False)

    def _default_ECP20_parasitas_2(self):
        return self._get_default('ECP20', 'ECP20-02-04')
    ECP20_parasitas_2 = fields.Char(
        'Parasitas (2):', readonly=False, default=_default_ECP20_parasitas_2
    )

    def _write_ECP20_parasitas_2(self):
        self._set_result('ECP20', 'ECP20-02-04', self.ECP20_lab_test_parasite_2_names)

    def _default_ECP20_lab_test_parasite_2_ids(self):
        LabTestParasite = self.env['clv.lab_test.parasite']
        parasite_ids = []
        if self._get_default('ECP20', 'ECP20-02-04') is not False:
            parasitas = self._get_default('ECP20', 'ECP20-02-04').split(', ')
            for parasita in parasitas:
                parasite = LabTestParasite.search([
                    ('name', '=', parasita),
                ])
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
        return parasite_ids
    ECP20_lab_test_parasite_2_ids = fields.Many2many(
        comodel_name='clv.lab_test.parasite',
        relation='clv_lab_test_parasite_2_lab_test_result_edit_ecp20_rel',
        string='Lab Test Parasites (2)',
        default=_default_ECP20_lab_test_parasite_2_ids
    )

    ECP20_lab_test_parasite_2_names = fields.Char(
        string='Parasitas (2)',
        compute='_compute_ECP20_lab_test_parasite_2_names',
        store=True
    )
    ECP20_lab_test_parasite_2_names_suport = fields.Char(
        string='Parasite Names Suport (2)',
        compute='_compute_ECP20_lab_test_parasite_2_names_suport',
        store=False
    )

    @api.depends('ECP20_lab_test_parasite_2_ids')
    def _compute_ECP20_lab_test_parasite_2_names(self):
        for r in self:
            r.ECP20_lab_test_parasite_2_names = r.ECP20_lab_test_parasite_2_names_suport

    @api.multi
    def _compute_ECP20_lab_test_parasite_2_names_suport(self):
        for r in self:
            ECP20_lab_test_parasite_2_names = False
            for parasite in r.ECP20_lab_test_parasite_2_ids:
                if ECP20_lab_test_parasite_2_names is False:
                    ECP20_lab_test_parasite_2_names = parasite.name
                else:
                    ECP20_lab_test_parasite_2_names = ECP20_lab_test_parasite_2_names + ', ' + parasite.name
            r.ECP20_lab_test_parasite_2_names_suport = ECP20_lab_test_parasite_2_names

    # Exame Coproparasitológico (3)

    def _default_ECP20_metodo_utilizado_3(self):
        return self._get_default('ECP20', 'ECP20-03-01')
    ECP20_metodo_utilizado_3 = fields.Selection([
        ('Ritchie', 'Ritchie'),
        ('Hoffmann', 'Hoffmann'),
        ('Faust', 'Faust'),
        ('Willis', 'Willis'),
    ], 'Metodologia Empregada (3)', readonly=False, default=_default_ECP20_metodo_utilizado_3)

    def _write_ECP20_metodo_utilizado_3(self):
        self._set_result('ECP20', 'ECP20-03-01', self.ECP20_metodo_utilizado_3)

    def _default_ECP20_resultado_3(self):
        return self._get_default('ECP20', 'ECP20-03-02')
    ECP20_resultado_3 = fields.Selection([
        ('POSITIVO', 'POSITIVO'),
        ('NEGATIVO', 'NEGATIVO'),
        ('Não realizado', 'Não realizado'),
    ], 'Resultado (3)', readonly=False, default=_default_ECP20_resultado_3)

    def _write_ECP20_resultado_3(self):
        self._set_result('ECP20', 'ECP20-03-02', self.ECP20_resultado_3)

    def _default_ECP20_examinador_3(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('ECP20', 'ECP20-03-03')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    ECP20_examinador_3 = fields.Many2one(
        'hr.employee',
        string='Examinador (3)',
        readonly=False,
        default=_default_ECP20_examinador_3
    )

    def _write_ECP20_examinador_3(self):
        if self.ECP20_examinador_3.name is not False:
            self._set_result(
                'ECP20', 'ECP20-03-03',
                self.ECP20_examinador_3.name + ' [' + self.ECP20_examinador_3.code + ']'
            )
        else:
            self._set_result('ECP20', 'ECP20-03-03', False)

    def _default_ECP20_parasitas_3(self):
        return self._get_default('ECP20', 'ECP20-03-04')
    ECP20_parasitas_3 = fields.Char(
        'Parasitas (3):', readonly=False, default=_default_ECP20_parasitas_3
    )

    def _write_ECP20_parasitas_3(self):
        self._set_result('ECP20', 'ECP20-03-04', self.ECP20_lab_test_parasite_3_names)

    def _default_ECP20_lab_test_parasite_3_ids(self):
        LabTestParasite = self.env['clv.lab_test.parasite']
        parasite_ids = []
        if self._get_default('ECP20', 'ECP20-03-04') is not False:
            parasitas = self._get_default('ECP20', 'ECP20-03-04').split(', ')
            for parasita in parasitas:
                parasite = LabTestParasite.search([
                    ('name', '=', parasita),
                ])
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
        return parasite_ids
    ECP20_lab_test_parasite_3_ids = fields.Many2many(
        comodel_name='clv.lab_test.parasite',
        relation='clv_lab_test_parasite_3_lab_test_result_edit_ecp20_rel',
        string='Lab Test Parasites (3)',
        default=_default_ECP20_lab_test_parasite_3_ids
    )

    ECP20_lab_test_parasite_3_names = fields.Char(
        string='Parasitas (3)',
        compute='_compute_ECP20_lab_test_parasite_3_names',
        store=True
    )
    ECP20_lab_test_parasite_3_names_suport = fields.Char(
        string='Parasite Names Suport (3)',
        compute='_compute_ECP20_lab_test_parasite_3_names_suport',
        store=False
    )

    @api.depends('ECP20_lab_test_parasite_3_ids')
    def _compute_ECP20_lab_test_parasite_3_names(self):
        for r in self:
            r.ECP20_lab_test_parasite_3_names = r.ECP20_lab_test_parasite_3_names_suport

    @api.multi
    def _compute_ECP20_lab_test_parasite_3_names_suport(self):
        for r in self:
            ECP20_lab_test_parasite_3_names = False
            for parasite in r.ECP20_lab_test_parasite_3_ids:
                if ECP20_lab_test_parasite_3_names is False:
                    ECP20_lab_test_parasite_3_names = parasite.name
                else:
                    ECP20_lab_test_parasite_3_names = ECP20_lab_test_parasite_3_names + ', ' + parasite.name
            r.ECP20_lab_test_parasite_3_names_suport = ECP20_lab_test_parasite_3_names

    # Exame Coproparasitológico (4)

    def _default_ECP20_metodo_utilizado_4(self):
        return self._get_default('ECP20', 'ECP20-04-01')
    # ECP20_metodo_utilizado_4 = fields.Selection([
    #     ('Ritchie', 'Ritchie'),
    #     ('Hoffmann', 'Hoffmann'),
    #     ('Faust', 'Faust'),
    #     ('Willis', 'Willis'),
    # ], 'Metodologia Empregada (4)', readonly=False, default=_default_ECP20_metodo_utilizado_4)
    ECP20_metodo_utilizado_4 = fields.Char(
        string='Metodologia Empregada (4)',
        default=_default_ECP20_metodo_utilizado_4,
    )

    def _write_ECP20_metodo_utilizado_4(self):
        self._set_result('ECP20', 'ECP20-04-01', self.ECP20_metodo_utilizado_4)

    def _default_ECP20_resultado_4(self):
        return self._get_default('ECP20', 'ECP20-04-02')
    ECP20_resultado_4 = fields.Selection([
        ('POSITIVO', 'POSITIVO'),
        ('NEGATIVO', 'NEGATIVO'),
        ('Não realizado', 'Não realizado'),
    ], 'Resultado (4)', readonly=False, default=_default_ECP20_resultado_4)

    def _write_ECP20_resultado_4(self):
        self._set_result('ECP20', 'ECP20-04-02', self.ECP20_resultado_4)

    def _default_ECP20_examinador_4(self):
        employee_model = self.env['hr.employee']
        code = self._get_default('ECP20', 'ECP20-04-03')
        if code is not False:
            code = code[code.find('[') + 1:code.find(']')]
            employee_search = employee_model.search([
                ('code', '=', code),
            ])
            return employee_search
        else:
            return False
    ECP20_examinador_4 = fields.Many2one(
        'hr.employee',
        string='Examinador (4)',
        readonly=False,
        default=_default_ECP20_examinador_4
    )

    def _write_ECP20_examinador_4(self):
        if self.ECP20_examinador_4.name is not False:
            self._set_result(
                'ECP20', 'ECP20-04-03',
                self.ECP20_examinador_4.name + ' [' + self.ECP20_examinador_4.code + ']'
            )
        else:
            self._set_result('ECP20', 'ECP20-04-03', False)

    def _default_ECP20_parasitas_4(self):
        return self._get_default('ECP20', 'ECP20-04-04')
    ECP20_parasitas_4 = fields.Char(
        'Parasitas (4):', readonly=False, default=_default_ECP20_parasitas_4
    )

    def _write_ECP20_parasitas_4(self):
        self._set_result('ECP20', 'ECP20-04-04', self.ECP20_lab_test_parasite_4_names)

    def _default_ECP20_lab_test_parasite_4_ids(self):
        LabTestParasite = self.env['clv.lab_test.parasite']
        parasite_ids = []
        if self._get_default('ECP20', 'ECP20-04-04') is not False:
            parasitas = self._get_default('ECP20', 'ECP20-04-04').split(', ')
            for parasita in parasitas:
                parasite = LabTestParasite.search([
                    ('name', '=', parasita),
                ])
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
        return parasite_ids
    ECP20_lab_test_parasite_4_ids = fields.Many2many(
        comodel_name='clv.lab_test.parasite',
        relation='clv_lab_test_parasite_4_lab_test_result_edit_ecp20_rel',
        string='Lab Test Parasites (4)',
        default=_default_ECP20_lab_test_parasite_4_ids
    )

    ECP20_lab_test_parasite_4_names = fields.Char(
        string='Parasitas (4)',
        compute='_compute_ECP20_lab_test_parasite_4_names',
        store=True
    )
    ECP20_lab_test_parasite_4_names_suport = fields.Char(
        string='Parasite Names Suport (4)',
        compute='_compute_ECP20_lab_test_parasite_4_names_suport',
        store=False
    )

    @api.depends('ECP20_lab_test_parasite_4_ids')
    def _compute_ECP20_lab_test_parasite_4_names(self):
        for r in self:
            r.ECP20_lab_test_parasite_4_names = r.ECP20_lab_test_parasite_4_names_suport

    @api.multi
    def _compute_ECP20_lab_test_parasite_4_names_suport(self):
        for r in self:
            ECP20_lab_test_parasite_4_names = False
            for parasite in r.ECP20_lab_test_parasite_4_ids:
                if ECP20_lab_test_parasite_4_names is False:
                    ECP20_lab_test_parasite_4_names = parasite.name
                else:
                    ECP20_lab_test_parasite_4_names = ECP20_lab_test_parasite_4_names + ', ' + parasite.name
            r.ECP20_lab_test_parasite_4_names_suport = ECP20_lab_test_parasite_4_names

    # Exame Coproparasitológico

    def _default_ECP20_data_entrada_material(self):
        return self._get_default('ECP20', 'ECP20-05-01')
    ECP20_data_entrada_material = fields.Date(
        'Data de Entrada do Material', readonly=False, default=_default_ECP20_data_entrada_material
    )

    def _write_ECP20_data_entrada_material(self):
        self._set_result('ECP20', 'ECP20-05-01', self.ECP20_data_entrada_material)

    def _default_ECP20_liberacao_resultado(self):
        return self._get_default('ECP20', 'ECP20-05-02')
    ECP20_liberacao_resultado = fields.Date(
        'Liberação do Resultado', readonly=False, default=_default_ECP20_liberacao_resultado
    )

    def _write_ECP20_liberacao_resultado(self):
        self._set_result('ECP20', 'ECP20-05-02', self.ECP20_liberacao_resultado)

    def _default_ECP20_metodos_utilizados(self):
        return self._get_default('ECP20', 'ECP20-05-03')
    ECP20_metodos_utilizados = fields.Char(
        string='Metodologia(s) Empregada(s)',
        default=_default_ECP20_metodos_utilizados,
        compute='_compute_ECP20_metodos_utilizados',
        store=True
    )

    def _write_ECP20_metodos_utilizados(self):
        self._set_result('ECP20', 'ECP20-05-03', self.ECP20_metodos_utilizados)

    def _default_ECP20_resultado(self):
        return self._get_default('ECP20', 'ECP20-05-04')
    ECP20_resultado = fields.Selection([
        ('POSITIVO', 'POSITIVO'),
        ('NEGATIVO', 'NEGATIVO'),
        ('Não realizado', 'Não realizado'),
    ],
        string='Resultado',
        readonly=False,
        default=_default_ECP20_resultado
    )

    def _write_ECP20_resultado(self):
        self._set_result('ECP20', 'ECP20-05-04', self.ECP20_resultado)

    def _default_ECP20_parasitas(self):
        return self._get_default('ECP20', 'ECP20-05-05')
    ECP20_parasitas = fields.Char(
        'Parasitas:', readonly=False, default=_default_ECP20_parasitas
    )

    def _write_ECP20_parasitas(self):
        self._set_result('ECP20', 'ECP20-05-05', self.ECP20_lab_test_parasite_names)

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
        relation='clv_lab_test_parasite_lab_test_result_edit_ecp20_rel_2',
        string='Lab Test Parasites',
        default=_default_ECP20_lab_test_parasite_ids,
        compute='_compute_ECP20_lab_test_parasite_ids',
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

    @api.depends(
        'ECP20_metodo_utilizado_1',
        'ECP20_metodo_utilizado_2',
        'ECP20_metodo_utilizado_3',
        'ECP20_metodo_utilizado_4',
    )
    def _compute_ECP20_metodos_utilizados(self):
        for r in self:
            ECP20_metodos_utilizados = False
            if r.ECP20_metodo_utilizado_1 is not False:
                ECP20_metodos_utilizados = r.ECP20_metodo_utilizado_1
                if r.ECP20_metodo_utilizado_2 is not False:
                    ECP20_metodos_utilizados = ECP20_metodos_utilizados + ', ' + r.ECP20_metodo_utilizado_2
                if r.ECP20_metodo_utilizado_3 is not False:
                    ECP20_metodos_utilizados = ECP20_metodos_utilizados + ', ' + r.ECP20_metodo_utilizado_3
                if r.ECP20_metodo_utilizado_4 is not False:
                    ECP20_metodos_utilizados = ECP20_metodos_utilizados + ', ' + r.ECP20_metodo_utilizado_4
            elif r.ECP20_metodo_utilizado_2 is not False:
                ECP20_metodos_utilizados = r.ECP20_metodo_utilizado_2
                if r.ECP20_metodo_utilizado_3 is not False:
                    ECP20_metodos_utilizados = ECP20_metodos_utilizados + ', ' + r.ECP20_metodo_utilizado_3
                if r.ECP20_metodo_utilizado_4 is not False:
                    ECP20_metodos_utilizados = ECP20_metodos_utilizados + ', ' + r.ECP20_metodo_utilizado_4
            elif r.ECP20_metodo_utilizado_3 is not False:
                ECP20_metodos_utilizados = r.ECP20_metodo_utilizado_3
                if r.ECP20_metodo_utilizado_4 is not False:
                    ECP20_metodos_utilizados = ECP20_metodos_utilizados + ', ' + r.ECP20_metodo_utilizado_4
            elif r.ECP20_metodo_utilizado_4 is not False:
                ECP20_metodos_utilizados = r.ECP20_metodo_utilizado_4
            r.ECP20_metodos_utilizados = ECP20_metodos_utilizados

    @api.depends(
        'ECP20_lab_test_parasite_1_ids',
        'ECP20_lab_test_parasite_2_ids',
        'ECP20_lab_test_parasite_3_ids',
        'ECP20_lab_test_parasite_4_ids',
    )
    def _compute_ECP20_lab_test_parasite_ids(self):
        parasite_ids = []
        for r in self:
            for parasite in self.ECP20_lab_test_parasite_1_ids:
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
            for parasite in self.ECP20_lab_test_parasite_2_ids:
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
            for parasite in self.ECP20_lab_test_parasite_3_ids:
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
            for parasite in self.ECP20_lab_test_parasite_4_ids:
                if parasite.id is not False:
                    parasite_ids.append((4, parasite.id))
            r.ECP20_lab_test_parasite_ids = parasite_ids

    def do_result_updt_ECP20(self):

        self._write_ECP20_metodo_utilizado_1()
        self._write_ECP20_resultado_1()
        self._write_ECP20_examinador_1()
        self._write_ECP20_parasitas_1()

        self._write_ECP20_metodo_utilizado_2()
        self._write_ECP20_resultado_2()
        self._write_ECP20_examinador_2()
        self._write_ECP20_parasitas_2()

        self._write_ECP20_metodo_utilizado_3()
        self._write_ECP20_resultado_3()
        self._write_ECP20_examinador_3()
        self._write_ECP20_parasitas_3()

        self._write_ECP20_metodo_utilizado_4()
        self._write_ECP20_resultado_4()
        self._write_ECP20_examinador_4()
        self._write_ECP20_parasitas_4()

        self._write_ECP20_data_entrada_material()
        self._write_ECP20_liberacao_resultado()
        self._write_ECP20_metodos_utilizados()
        self._write_ECP20_resultado()
        self._write_ECP20_parasitas()
        self._write_ECP20_obs()

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
