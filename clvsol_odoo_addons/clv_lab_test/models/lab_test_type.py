# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields, models


class LabTestType (models.Model):
    _description = 'Lab Test Type'
    _name = 'clv.lab_test.type'
    _order = 'name'

    name = fields.Char(string='Lab Test Type', required=True)
    code = fields.Char(string='Lab Test Type Code')

    notes = fields.Text(string='Notes')

    date_inclusion = fields.Date(
        string='Inclusion Date',
        default=lambda *a: datetime.now().strftime('%Y-%m-%d')
    )

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),

        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]
