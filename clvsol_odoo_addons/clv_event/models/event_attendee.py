# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EventAttendee(models.Model):
    _description = 'Event Attendee'
    _name = 'clv.event.attendee'

    event_id = fields.Many2one(
        comodel_name='clv.event',
        string='Event',
        required=False
    )

    notes = fields.Text(string='Notes')


class Event(models.Model):
    _inherit = 'clv.event'

    event_attendee_ids = fields.One2many(
        comodel_name='clv.event.attendee',
        inverse_name='event_id',
        string='Attendees',
        readonly=True
    )
    count_event_attendees = fields.Integer(
        string='Number of Attendees',
        compute='_compute_count_event_attendees',
        store=False
    )

    @api.depends('event_attendee_ids')
    def _compute_count_event_attendees(self):
        for r in self:
            r.count_event_attendees = len(r.event_attendee_ids)
