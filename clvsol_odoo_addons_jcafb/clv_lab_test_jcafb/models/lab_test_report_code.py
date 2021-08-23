# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LabTestReport(models.Model):
    _name = "clv.lab_test.report"
    _inherit = 'clv.lab_test.report', 'clv.abstract.code'

    code = fields.Char(string='Lab Test Report Code', required=False, default='/')
    code_sequence = fields.Char(default='clv.lab_test.report.code')
