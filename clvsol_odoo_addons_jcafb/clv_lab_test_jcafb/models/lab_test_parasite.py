# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LabTestParasite(models.Model):
    _description = 'Lab Test Parasite'
    _name = 'clv.lab_test.parasite'
    _order = 'name'

    name = fields.Char(string='Parasite', required=True)

    part1 = fields.Char(string='Part 1', required=False)
    part2 = fields.Char(string='Part 2', required=False)

    code = fields.Char(string='Parasite Code', required=False)

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE(name)',
         u'Error! The Parasite must be unique!'
         ),
        ('code_uniq',
         'UNIQUE(code)',
         u'Error! The Parasite Code must be unique!'
         ),
    ]
