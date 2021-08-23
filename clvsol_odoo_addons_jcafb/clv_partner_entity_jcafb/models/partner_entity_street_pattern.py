# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PartnerEntityStreetPattern(models.Model):
    _description = 'Partner Entity Street Pattern'
    _name = "clv.partner_entity.street_pattern"
    _order = "street, district"
    _rec_name = 'street'

    @api.multi
    @api.depends('street', 'district')
    def name_get(self):
        result = []
        for record in self:
            if record.district:
                result.append(
                    (record.id,
                     u'%s (%s)' % (record.street, record.district)
                     ))
            else:
                result.append(
                    (record.id,
                     u'%s' % (record.street)
                     ))
        return result

    street = fields.Char(string='Street')

    district = fields.Char(string='District')

    notes = fields.Text(string='Notes')

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('pattern_uniq',
         'UNIQUE(street, district)',
         u'Error! The Pattern must be unique!'
         ),
    ]
