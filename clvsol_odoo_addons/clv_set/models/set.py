# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Set(models.Model):
    _description = 'Set'
    _name = 'clv.set'
    _order = 'name'

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for record in self:
            if record.code is not False:
                result.append(
                    (record.id,
                     u'%s [%s]' % (record.name, record.code)
                     ))
            else:
                result.append(
                    (record.id,
                     u'%s' % (record.name)
                     ))
        return result

    name = fields.Char(string='Set Name', required=True, help="Set Name")

    code = fields.Char(string='Set Code', required=False)

    notes = fields.Text(string='Notes')

    date_inclusion = fields.Datetime(
        string='Inclusion Date',
        default=fields.Datetime.now)

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]
