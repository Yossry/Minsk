# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LabTestCrystal(models.Model):
    _description = 'Lab Test Crystal'
    _name = 'clv.lab_test.crystal'
    _order = 'name'

    name = fields.Char(string='Crystal', required=True)

    code = fields.Char(string='Crystal Code', required=False)

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE(name)',
         u'Error! The Crystal must be unique!'
         ),
        ('code_uniq',
         'UNIQUE(code)',
         u'Error! The Crystal Code must be unique!'
         ),
    ]
