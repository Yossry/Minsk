# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from datetime import datetime

from odoo import fields, models


class LabTestReport(models.Model):
    _description = 'Lab Test Report'
    _name = "clv.lab_test.report"
    _rec_name = 'code'
    _order = 'code'

    code = fields.Char(string='Lab Test Report Code')

    lab_test_type_id = fields.Many2one(comodel_name='clv.lab_test.type', string='Lab Test Type')
    lab_test_type_code = fields.Char(string='Lab Test Type Code', related='lab_test_type_id.code', store=False)
    lab_test_request_id = fields.Many2one(comodel_name='clv.lab_test.request', string='Lab Test Request')

    date_report = fields.Datetime(
        string='Date of the Report',
        # default=lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]


class LabTestType(models.Model):
    _inherit = 'clv.lab_test.type'

    lab_test_report_ids = fields.One2many(
        comodel_name='clv.lab_test.report',
        inverse_name='lab_test_type_id',
        string='Lab Test Reports'
    )


class LabTestRequest(models.Model):
    _inherit = 'clv.lab_test.request'

    lab_test_report_ids = fields.One2many(
        comodel_name='clv.lab_test.report',
        inverse_name='lab_test_request_id',
        string='Lab Test Reports'
    )
