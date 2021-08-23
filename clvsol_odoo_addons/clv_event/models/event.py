# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Event(models.Model):
    _description = 'Event'
    _name = 'clv.event'
    _order = 'name'

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id,
                 u'%s [%s]' % (record.name, record.code)
                 ))
        return result

    name = fields.Char(string='Event Name', required=True, help="Event Name")

    code = fields.Char(string='Event Code', required=False)

    sequence = fields.Integer(
        string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of events.")
    planned_hours = fields.Float(
        string='Planned Hours',
        help='Estimated time (in hours) to do the event.'
    )

    notes = fields.Text(string='Notes')

    date_inclusion = fields.Datetime(
        string='Inclusion Date',
        default=fields.Datetime.now)
    date_foreseen = fields.Datetime(string='Foreseen Date', index=True, copy=False)
    date_start = fields.Datetime(string='Starting Date', index=True, copy=False)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False)

    active = fields.Boolean(string='Active', default=1)

    _sql_constraints = [
        ('code_uniq',
         'UNIQUE (code)',
         u'Error! The Code must be unique!'),
    ]
