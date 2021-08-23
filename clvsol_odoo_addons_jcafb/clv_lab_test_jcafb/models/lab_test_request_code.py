# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LabTestRequest(models.Model):
    _name = "clv.lab_test.request"
    _inherit = 'clv.lab_test.request', 'clv.abstract.code'

    code = fields.Char(string='Lab Test Request Code', required=False, default='/')
    code_sequence = fields.Char(default='clv.lab_test.request.code')
