# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    code = fields.Char(string='Question Code', required=False)

    parameter = fields.Char(string='Related Parameter', required=False)

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Question Code must be unique!'),
    ]
