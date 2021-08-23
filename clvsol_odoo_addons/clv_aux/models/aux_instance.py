# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AuxInstance(models.Model):
    _description = 'Auxiliary Instance'
    _name = 'clv.aux.instance'
    _order = 'name'

    name = fields.Char(string='Name', required=True)

    code = fields.Char(string='Auxiliary Instance Code', required=False)

    instance_default = fields.Boolean(string='Default Instance', default=False)

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         u'Error! The Name must be unique!'),
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]
