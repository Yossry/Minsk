# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LabTestTypeCriterion(models.Model):
    _description = 'Lab Test Criterion'
    _name = "clv.lab_test.criterion"
    _order = "sequence"

    code = fields.Char(string='Criterion Code')
    name = fields.Char(string='Test')

    # result = fields.Text('Results')
    result = fields.Char(sring='Results')
    unit_id = fields.Many2one(comodel_name='clv.lab_test.unit', string='Unit')
    normal_range = fields.Text(string='Normal Range')

    lab_test_type_id = fields.Many2one(comodel_name='clv.lab_test.type', string='Test Type')

    lab_test_result_id = fields.Many2one(comodel_name='clv.lab_test.result', string='Test Result')

    lab_test_report_id = fields.Many2one(comodel_name='clv.lab_test.report', string='Test Report')

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    result_display = fields.Boolean(string='Display in Result', default=True)
    report_display = fields.Boolean(string='Display in Report', default=True)

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('type_code_uniq',
         'UNIQUE(lab_test_type_id, code)',
         u'Error! The Code must be unique for a Test Type!'
         ),
        ('result_code_uniq',
         'UNIQUE(lab_test_result_id, code)',
         u'Error! The Code must be unique for a Test Result!'
         ),
        ('report_code_uniq',
         'UNIQUE(lab_test_report_id, code)',
         u'Error! The Code must be unique for a Test Report!'
         ),
    ]


class LabTestType(models.Model):
    _inherit = 'clv.lab_test.type'

    criterion_ids = fields.One2many(
        comodel_name='clv.lab_test.criterion',
        inverse_name='lab_test_type_id',
        string='Test Cases'
    )


class LabTestResult(models.Model):
    _inherit = 'clv.lab_test.result'

    criterion_ids = fields.One2many(
        comodel_name='clv.lab_test.criterion',
        inverse_name='lab_test_result_id',
        readonly=True,
        string='Test Cases'
    )


class LabTestReport(models.Model):
    _inherit = 'clv.lab_test.report'

    criterion_ids = fields.One2many(
        comodel_name='clv.lab_test.criterion',
        inverse_name='lab_test_report_id',
        readonly=True,
        string='Test Cases'
    )
