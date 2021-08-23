# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    @api.depends('name', 'code', 'professional_id')
    def name_get(self):
        result = []
        for record in self:
            if record.professional_id is not False:
                if record.code is not False:
                    result.append(
                        (record.id,
                         u'%s [%s] (%s)' % (record.name, record.code, record.professional_id)
                         ))
                else:
                    result.append(
                        (record.id,
                         u'%s (%s)' % (record.name, record.professional_id)
                         ))
            else:
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

    code = fields.Char(string='Employee Code', required=False)

    professional_id = fields.Char(string='Professional ID', required=False)

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),

        ('professional_id_uniq',
         'UNIQUE (professional_id)',
         u'Error! The Professional ID must be unique!'),
    ]
