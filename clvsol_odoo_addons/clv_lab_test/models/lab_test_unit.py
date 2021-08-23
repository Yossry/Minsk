# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LabTestUnit(models.Model):
    _description = 'Lab Test Unit'
    _name = "clv.lab_test.unit"

    name = fields.Char(
        string='Unit',
        required=True,
        help='Unit for Lab Test Criteria'
    )
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),

        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]
