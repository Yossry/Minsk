# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Insured(models.Model):
    _name = "clv.insured"
    _inherit = 'clv.insured', 'clv.abstract.code'

    code = fields.Char(string='Insured Code', required=False, default='/')
    code_sequence = fields.Char(default='clv.insured.code')
