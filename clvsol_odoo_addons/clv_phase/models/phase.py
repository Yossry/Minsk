# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Phase(models.Model):
    _description = 'Phase'
    _name = 'clv.phase'
    _order = 'name'

    name = fields.Char(string='Phase', required=True, translate=True)
    code = fields.Char(string='Phase Code', required=False)
    description = fields.Char(string='Description')
    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Error! The Phase must be unique!'),
        ('code_uniq',
         'UNIQUE (code)',
         'Error! The Code must be unique!'),
    ]
