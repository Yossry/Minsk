# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveyLabel(models.Model):
    _inherit = 'survey.label'

    code = fields.Char(string='Label Code', required=False)

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Label Code must be unique!'),
    ]
