# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class LabTestResultCopyToReportEUR20(models.TransientModel):
    _description = 'Lab Test Result Copy to Report (EUR20)'
    _name = 'clv.lab_test.result.copy_to_report_eur20'

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
    # EUR20
    #

    def _default_EUR20_volume(self):
        return self._get_default('EUR20', 'EUR20-02-01')
    EUR20_volume = fields.Char(
        'Volume', readonly=False, default=_default_EUR20_volume
    )

    def _write_EUR20_volume(self):
        self._set_result('EUR20', 'EUR20-02-01', self.EUR20_volume)
        self._copy_result('EUR20', 'EUR20-02-01', self.EUR20_volume)

    def _default_EUR20_densidade(self):
        return self._get_default('EUR20', 'EUR20-02-02')
    EUR20_densidade = fields.Char(
        'Densidade', readonly=False, default=_default_EUR20_densidade
    )

    def _write_EUR20_densidade(self):
        self._set_result('EUR20', 'EUR20-02-02', self.EUR20_densidade)
        self._copy_result('EUR20', 'EUR20-02-02', self.EUR20_densidade)

    def _default_EUR20_aspecto(self):
        return self._get_default('EUR20', 'EUR20-02-03')
    EUR20_aspecto = fields.Selection([
        (u'Límpido', u'Límpido'),
        (u'Ligeiramente Turvo', u'Ligeiramente Turvo'),
        (u'Turvo', u'Turvo'),
    ], 'Aspecto', readonly=False, default=_default_EUR20_aspecto)

    def _write_EUR20_aspecto(self):
        self._set_result('EUR20', 'EUR20-02-03', self.EUR20_aspecto)
        self._copy_result('EUR20', 'EUR20-02-03', self.EUR20_aspecto)

    def _default_EUR20_cor(self):
        return self._get_default('EUR20', 'EUR20-02-04')
    EUR20_cor = fields.Selection([
        (u'Amarela Palha', u'Amarela Palha'),
        (u'Amarela Claro', u'Amarela Claro'),
        (u'Amarela Citrino', u'Amarela Citrino'),
        (u'Amarela Ouro', u'Amarela Ouro'),
        (u'Eritrocrômica', u'Eritrocrômica'),
        (u'Âmbar', u'Âmbar'),
    ], 'Cor', readonly=False, default=_default_EUR20_cor)

    def _write_EUR20_cor(self):
        self._set_result('EUR20', 'EUR20-02-04', self.EUR20_cor)
        self._copy_result('EUR20', 'EUR20-02-04', self.EUR20_cor)

    def _default_EUR20_odor(self):
        return self._get_default('EUR20', 'EUR20-02-05')
    EUR20_odor = fields.Selection([
        (u'Sui Generis', u'Sui Generis'),
        (u'Pútrido', u'Pútrido'),
    ], 'Odor', readonly=False, default=_default_EUR20_odor)

    def _write_EUR20_odor(self):
        self._set_result('EUR20', 'EUR20-02-05', self.EUR20_odor)
        self._copy_result('EUR20', 'EUR20-02-05', self.EUR20_odor)

    def _default_EUR20_ph(self):
        return self._get_default('EUR20', 'EUR20-03-01')
    EUR20_ph = fields.Char(
        'pH', readonly=False, default=_default_EUR20_ph
    )

    def _write_EUR20_ph(self):
        self._set_result('EUR20', 'EUR20-03-01', self.EUR20_ph)
        self._copy_result('EUR20', 'EUR20-03-01', self.EUR20_ph)

    def _default_EUR20_proteinas(self):
        return self._get_default('EUR20', 'EUR20-03-02')
    EUR20_proteinas = fields.Selection([
        (u'Negativo', u'Negativo'),
        (u'Traços', u'Traços'),
        ('(+)', '(+)'),
        ('(++)', '(++)'),
        ('(+++)', '(+++)'),
        ('(++++)', '(++++)'),
    ], 'Proteina', readonly=False, default=_default_EUR20_proteinas)

    def _write_EUR20_proteinas(self):
        self._set_result('EUR20', 'EUR20-03-02', self.EUR20_proteinas)
        self._copy_result('EUR20', 'EUR20-03-02', self.EUR20_proteinas)

    def _default_EUR20_glicose(self):
        return self._get_default('EUR20', 'EUR20-03-03')
    EUR20_glicose = fields.Selection([
        (u'Negativo', u'Negativo'),
        (u'Traços', u'Traços'),
        ('(+)', '(+)'),
        ('(++)', '(++)'),
        ('(+++)', '(+++)'),
        ('(++++)', '(++++)'),
    ], 'Glicose', readonly=False, default=_default_EUR20_glicose)

    def _write_EUR20_glicose(self):
        self._set_result('EUR20', 'EUR20-03-03', self.EUR20_glicose)
        self._copy_result('EUR20', 'EUR20-03-03', self.EUR20_glicose)

    def _default_EUR20_cetona(self):
        return self._get_default('EUR20', 'EUR20-03-04')
    EUR20_cetona = fields.Selection([
        (u'Negativo', u'Negativo'),
        (u'Traços', u'Traços'),
        ('(+)', '(+)'),
        ('(++)', '(++)'),
        ('(+++)', '(+++)'),
        ('(++++)', '(++++)'),
    ], 'Cetona', readonly=False, default=_default_EUR20_cetona)

    def _write_EUR20_cetona(self):
        self._set_result('EUR20', 'EUR20-03-04', self.EUR20_cetona)
        self._copy_result('EUR20', 'EUR20-03-04', self.EUR20_cetona)

    def _default_EUR20_pigmentos_biliares(self):
        return self._get_default('EUR20', 'EUR20-03-05')
    EUR20_pigmentos_biliares = fields.Selection([
        (u'Negativo', u'Negativo'),
        (u'Traços', u'Traços'),
        ('(+)', '(+)'),
        ('(++)', '(++)'),
        ('(+++)', '(+++)'),
        ('(++++)', '(++++)'),
    ], 'Pigmentos biliares', readonly=False, default=_default_EUR20_pigmentos_biliares)

    def _write_EUR20_pigmentos_biliares(self):
        self._set_result('EUR20', 'EUR20-03-05', self.EUR20_pigmentos_biliares)
        self._copy_result('EUR20', 'EUR20-03-05', self.EUR20_pigmentos_biliares)

    def _default_EUR20_sangue(self):
        return self._get_default('EUR20', 'EUR20-03-06')
    EUR20_sangue = fields.Selection([
        (u'Negativo', u'Negativo'),
        (u'Traços', u'Traços'),
        ('(+)', '(+)'),
        ('(++)', '(++)'),
        ('(+++)', '(+++)'),
        ('(++++)', '(++++)'),
    ], 'Sangue', readonly=False, default=_default_EUR20_sangue)

    def _write_EUR20_sangue(self):
        self._set_result('EUR20', 'EUR20-03-06', self.EUR20_sangue)
        self._copy_result('EUR20', 'EUR20-03-06', self.EUR20_sangue)

    def _default_EUR20_urobilinogenio(self):
        return self._get_default('EUR20', 'EUR20-03-07')
    EUR20_urobilinogenio = fields.Selection([
        (u'Normal', u'Normal'),
        (u'Positivo até Diluição de 1/20', u'Positivo até Diluição de 1/20'),
        (u'Positivo até Diluição de 1/40', u'Positivo até Diluição de 1/40'),
        (u'Positivo até Diluição de 1/80', u'Positivo até Diluição de 1/80'),
        (u'Positivo até Diluição de 1/160', u'Positivo até Diluição de 1/160'),
        (u'Positivo até Diluição de 1/320', u'Positivo até Diluição de 1/320'),
        (u'Positivo até Diluição de 1/640', u'Positivo até Diluição de 1/640'),
        (u'Positivo até Diluição de 1/1280', u'Positivo até Diluição de 1/1280'),
        (u'Positivo até Diluição de 1/2560', u'Positivo até Diluição de 1/2560'),
    ], 'Urobilinogênio', readonly=False, default=_default_EUR20_urobilinogenio)

    def _write_EUR20_urobilinogenio(self):
        self._set_result('EUR20', 'EUR20-03-07', self.EUR20_urobilinogenio)
        self._copy_result('EUR20', 'EUR20-03-07', self.EUR20_urobilinogenio)

    def _default_EUR20_nitrito(self):
        return self._get_default('EUR20', 'EUR20-03-08')
    EUR20_nitrito = fields.Selection([
        (u'Negativo', u'Negativo'),
        (u'Positivo', u'Positivo'),
    ], 'Nitrito', readonly=False, default=_default_EUR20_nitrito)

    def _write_EUR20_nitrito(self):
        self._set_result('EUR20', 'EUR20-03-08', self.EUR20_nitrito)
        self._copy_result('EUR20', 'EUR20-03-08', self.EUR20_nitrito)

    def _default_EUR20_celulas_epiteliais(self):
        return self._get_default('EUR20', 'EUR20-04-01')
    EUR20_celulas_epiteliais = fields.Selection([
        (u'Ausentes', u'Ausentes'),
        (u'Raras', u'Raras'),
        (u'Frequentes', u'Frequentes'),
        (u'Numerosas', u'Numerosas'),
    ], 'Células Epiteliais', readonly=False, default=_default_EUR20_celulas_epiteliais)

    def _write_EUR20_celulas_epiteliais(self):
        self._set_result('EUR20', 'EUR20-04-01', self.EUR20_celulas_epiteliais)
        self._copy_result('EUR20', 'EUR20-04-01', self.EUR20_celulas_epiteliais)

    def _default_EUR20_muco(self):
        return self._get_default('EUR20', 'EUR20-04-02')
    EUR20_muco = fields.Selection([
        (u'Ausente', u'Ausente'),
        (u'Raros Filamentos', u'Raros Filamentos'),
        (u'Frequentes Filamentos', u'Frequentes Filamentos'),
        (u'Numerosos Filamentos', u'Numerosos Filamentos'),
    ], 'Muco', readonly=False, default=_default_EUR20_muco)

    def _write_EUR20_muco(self):
        self._set_result('EUR20', 'EUR20-04-02', self.EUR20_muco)
        self._copy_result('EUR20', 'EUR20-04-02', self.EUR20_muco)

    def _default_EUR20_leucocitos(self):
        return self._get_default('EUR20', 'EUR20-04-04')
    EUR20_leucocitos = fields.Char(
        'Leucócitos', readonly=False, default=_default_EUR20_leucocitos
    )

    def _write_EUR20_leucocitos(self):
        self._set_result('EUR20', 'EUR20-04-04', self.EUR20_leucocitos)
        self._copy_result('EUR20', 'EUR20-04-04', self.EUR20_leucocitos)

    def _default_EUR20_hemacias(self):
        return self._get_default('EUR20', 'EUR20-04-05')
    EUR20_hemacias = fields.Char(
        'Hemácias', readonly=False, default=_default_EUR20_hemacias
    )

    def _write_EUR20_hemacias(self):
        self._set_result('EUR20', 'EUR20-04-05', self.EUR20_hemacias)
        self._copy_result('EUR20', 'EUR20-04-05', self.EUR20_hemacias)

    def _default_EUR20_cilindros(self):
        return self._get_default('EUR20', 'EUR20-04-06')
    EUR20_cilindros = fields.Selection([
        (u'Ausentes', u'Ausentes'),
        (u'Presentes', u'Presentes'),
    ], 'Cilindros', readonly=False, default=_default_EUR20_cilindros)

    def _write_EUR20_cilindros(self):
        self._set_result('EUR20', 'EUR20-04-06', self.EUR20_cilindros)
        self._copy_result('EUR20', 'EUR20-04-06', self.EUR20_cilindros)

    def _default_EUR20_cilindros_hialinos(self):
        return self._get_default('EUR20', 'EUR20-04-07')
    EUR20_cilindros_hialinos = fields.Char(
        'Cilindros Hialinos', readonly=False, default=_default_EUR20_cilindros_hialinos
    )

    def _write_EUR20_cilindros_hialinos(self):
        self._set_result('EUR20', 'EUR20-04-07', self.EUR20_cilindros_hialinos)
        self._copy_result('EUR20', 'EUR20-04-07', self.EUR20_cilindros_hialinos)

    def _default_EUR20_cilindros_granulosos(self):
        return self._get_default('EUR20', 'EUR20-04-08')
    EUR20_cilindros_granulosos = fields.Char(
        'Cilindros Granulosos', readonly=False, default=_default_EUR20_cilindros_granulosos
    )

    def _write_EUR20_cilindros_granulosos(self):
        self._set_result('EUR20', 'EUR20-04-08', self.EUR20_cilindros_granulosos)
        self._copy_result('EUR20', 'EUR20-04-08', self.EUR20_cilindros_granulosos)

    def _default_EUR20_cilindros_leucocitarios(self):
        return self._get_default('EUR20', 'EUR20-04-09')
    EUR20_cilindros_leucocitarios = fields.Char(
        'Cilindros Leucocitários', readonly=False, default=_default_EUR20_cilindros_leucocitarios
    )

    def _write_EUR20_cilindros_leucocitarios(self):
        self._set_result('EUR20', 'EUR20-04-09', self.EUR20_cilindros_leucocitarios)
        self._copy_result('EUR20', 'EUR20-04-09', self.EUR20_cilindros_leucocitarios)

    def _default_EUR20_cilindros_hematicos(self):
        return self._get_default('EUR20', 'EUR20-04-10')
    EUR20_cilindros_hematicos = fields.Char(
        'Cilindros Hemáticos', readonly=False, default=_default_EUR20_cilindros_hematicos
    )

    def _write_EUR20_cilindros_hematicos(self):
        self._set_result('EUR20', 'EUR20-04-10', self.EUR20_cilindros_hematicos)
        self._copy_result('EUR20', 'EUR20-04-10', self.EUR20_cilindros_hematicos)

    def _default_EUR20_cilindros_cereos(self):
        return self._get_default('EUR20', 'EUR20-04-11')
    EUR20_cilindros_cereos = fields.Char(
        'Cilindros Céreos', readonly=False, default=_default_EUR20_cilindros_cereos
    )

    def _write_EUR20_cilindros_cereos(self):
        self._set_result('EUR20', 'EUR20-04-11', self.EUR20_cilindros_cereos)
        self._copy_result('EUR20', 'EUR20-04-11', self.EUR20_cilindros_cereos)

    def _default_EUR20_outros_tipos_de_cilindros(self):
        return self._get_default('EUR20', 'EUR20-04-12')
    EUR20_outros_tipos_de_cilindros = fields.Char(
        'Outros tipos de Cilindros', readonly=False, default=_default_EUR20_outros_tipos_de_cilindros
    )

    def _write_EUR20_outros_tipos_de_cilindros(self):
        self._set_result('EUR20', 'EUR20-04-12', self.EUR20_outros_tipos_de_cilindros)
        self._copy_result('EUR20', 'EUR20-04-12', self.EUR20_outros_tipos_de_cilindros)

    def _default_EUR20_obs(self):
        return self._get_default('EUR20', 'EUR20-05-01')
    EUR20_obs = fields.Char(
        'Observações', readonly=False, default=_default_EUR20_obs
    )

    def _write_EUR20_obs(self):
        self._set_result('EUR20', 'EUR20-05-01', self.EUR20_obs)
        self._copy_result('EUR20', 'EUR20-05-01', self.EUR20_obs)

    def _default_EUR20_cristais(self):
        return self._get_default('EUR20', 'EUR20-04-03')
    EUR20_cristais = fields.Char(
        'Cristais:', readonly=False, default=_default_EUR20_cristais
    )

    def _write_EUR20_cristais(self):
        self._set_result('EUR20', 'EUR20-04-03', self.EUR20_lab_test_crystal_names)
        self._copy_result('EUR20', 'EUR20-04-03', self.EUR20_lab_test_crystal_names)

    def _default_EUR20_lab_test_crystal_ids(self):
        LabTestCrystal = self.env['clv.lab_test.crystal']
        crystal_ids = []
        if self._get_default('EUR20', 'EUR20-04-03') is not False:
            cristais = self._get_default('EUR20', 'EUR20-04-03').split(', ')
            for cristal in cristais:
                crystal = LabTestCrystal.search([
                    ('name', '=', cristal),
                ])
                if crystal.id is not False:
                    crystal_ids.append((4, crystal.id))
        return crystal_ids
    EUR20_lab_test_crystal_ids = fields.Many2many(
        comodel_name='clv.lab_test.crystal',
        relation='clv_lab_test_crystal_lab_test_result_copy_to_report_rel',
        string='Lab Test Crystals',
        default=_default_EUR20_lab_test_crystal_ids
    )

    EUR20_lab_test_crystal_names = fields.Char(
        string='Cristais',
        compute='_compute_EUR20_lab_test_crystal_names',
        store=True
    )
    EUR20_lab_test_crystal_names_suport = fields.Char(
        string='Crystal Names Suport',
        compute='_compute_EUR20_lab_test_crystal_names_suport',
        store=False
    )

    @api.depends('EUR20_lab_test_crystal_ids')
    def _compute_EUR20_lab_test_crystal_names(self):
        for r in self:
            r.EUR20_lab_test_crystal_names = r.EUR20_lab_test_crystal_names_suport

    @api.multi
    def _compute_EUR20_lab_test_crystal_names_suport(self):
        for r in self:
            EUR20_lab_test_crystal_names = False
            for crystal in r.EUR20_lab_test_crystal_ids:
                if EUR20_lab_test_crystal_names is False:
                    EUR20_lab_test_crystal_names = crystal.name
                else:
                    EUR20_lab_test_crystal_names = EUR20_lab_test_crystal_names + ', ' + crystal.name
            r.EUR20_lab_test_crystal_names_suport = EUR20_lab_test_crystal_names
            # if r.EUR20_lab_test_crystal_names != EUR20_lab_test_crystal_names:
            #     record = self.env['clv.lab_test.report.edit'].search([('id', '=', r.id)])
            #     record.write({'EUR20_lab_test_crystal_ids': r.EUR20_lab_test_crystal_ids})

    def do_result_copy_to_report_EUR20(self):

        self._write_EUR20_volume()
        self._write_EUR20_densidade()
        self._write_EUR20_aspecto()
        self._write_EUR20_cor()
        self._write_EUR20_odor()
        self._write_EUR20_ph()
        self._write_EUR20_proteinas()
        self._write_EUR20_glicose()
        self._write_EUR20_cetona()
        self._write_EUR20_pigmentos_biliares()
        self._write_EUR20_sangue()
        self._write_EUR20_urobilinogenio()
        self._write_EUR20_nitrito()
        self._write_EUR20_celulas_epiteliais()
        self._write_EUR20_muco()
        self._write_EUR20_cristais()
        self._write_EUR20_leucocitos()
        self._write_EUR20_hemacias()
        self._write_EUR20_cilindros()
        self._write_EUR20_cilindros_hialinos()
        self._write_EUR20_cilindros_granulosos()
        self._write_EUR20_cilindros_leucocitarios()
        self._write_EUR20_cilindros_hematicos()
        self._write_EUR20_cilindros_cereos()
        self._write_EUR20_outros_tipos_de_cilindros()
        self._write_EUR20_obs()

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
